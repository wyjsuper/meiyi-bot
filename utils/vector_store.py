import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
import json
import time

class VectorStore:
    """向量存储管理器，用于管理和检索文档向量"""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.logger = logging.getLogger(__name__)

        # 确保持久化目录存在
        os.makedirs(persist_directory, exist_ok=True)

        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(path=persist_directory)

        # 使用SentenceTransformers作为嵌入函数
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="qa_pairs",
            metadata={"description": "问答对向量集合"}
        )

        self.logger.info("向量存储初始化完成")

    def add_documents(self, qa_pairs: List[Dict[str, Any]]):
        """
        添加文档到向量存储

        Args:
            qa_pairs: 问答对列表
        """
        try:
            # 准备文档
            documents = []
            metadatas = []
            ids = []

            for pair in qa_pairs:
                # 合并问题和答案作为文档内容
                content = f"问题: {pair['question']} 答案: {pair['answer']}"
                documents.append(content)

                # 元数据
                metadata = {
                    'question': pair['question'],
                    'answer': pair['answer'],
                    'source': pair['source'],
                    'question_id': str(pair['id'])
                }
                if 'metadata' in pair:
                    metadata.update(pair['metadata'])

                metadatas.append(metadata)
                ids.append(str(pair['id']))

            # 添加到集合
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            self.logger.info(f"成功添加 {len(qa_pairs)} 个文档到向量存储")

        except Exception as e:
            self.logger.error(f"添加文档失败: {e}")
            raise

    def search(self, query: str, k: int = 5, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        搜索相似文档

        Args:
            query: 查询文本
            k: 返回结果数量
            threshold: 相似度阈值

        Returns:
            匹配的文档列表
        """
        try:
            # 执行搜索
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                include=['documents', 'metadatas', 'distances']
            )

            # 处理结果
            matched_docs = []
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i]
                if distance <= (1 - threshold):  # 转换为相似度
                    doc = {
                        'id': results['ids'][0][i],
                        'question': results['metadatas'][0][i]['question'],
                        'answer': results['metadatas'][0][i]['answer'],
                        'source': results['metadatas'][0][i]['source'],
                        'distance': distance,
                        'similarity': 1 - distance,
                        'metadata': results['metadatas'][0][i]
                    }
                    matched_docs.append(doc)

            # 按相似度排序
            matched_docs.sort(key=lambda x: x['similarity'], reverse=True)

            self.logger.info(f"搜索完成，找到 {len(matched_docs)} 个相似文档")
            return matched_docs

        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            return []

    def get_document_count(self) -> int:
        """获取文档总数"""
        try:
            return self.collection.count()
        except Exception as e:
            self.logger.error(f"获取文档数量失败: {e}")
            return 0

    def clear_collection(self):
        """清空集合"""
        try:
            self.client.delete_collection(name="qa_pairs")
            self.collection = self.client.get_or_create_collection(
                name="qa_pairs",
                metadata={"description": "问答对向量集合"}
            )
            self.logger.info("向量存储已清空")
        except Exception as e:
            self.logger.error(f"清空集合失败: {e}")

    def save_metadata(self, metadata: Dict[str, Any]):
        """保存元数据"""
        try:
            metadata_path = os.path.join(self.persist_directory, "metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            self.logger.info("元数据已保存")
        except Exception as e:
            self.logger.error(f"保存元数据失败: {e}")

    def load_metadata(self) -> Dict[str, Any]:
        """加载元数据"""
        try:
            metadata_path = os.path.join(self.persist_directory, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"加载元数据失败: {e}")
            return {}
#!/usr/bin/env python3
"""
最终验证测试
"""

import os
import json
import re
from typing import List, Dict, Any

class SimpleHighlighter:
    """简单的关键词高亮器"""

    def highlight_keywords(self, text: str, keywords: List[str]) -> str:
        """高亮关键词"""
        if not keywords:
            return text

        for keyword in keywords:
            if keyword:
                text = re.sub(
                    re.escape(keyword),
                    f'<mark style="background-color: #ffff00; padding: 2px 4px; border-radius: 3px;">{keyword}</mark>',
                    text,
                    flags=re.IGNORECASE
                )
        return text

    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text)
        stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        keywords = []
        for word in words:
            if len(word) >= 2 and word not in stopwords and word not in keywords:
                keywords.append(word)
        return keywords[:5]

class SimpleParser:
    """简化的文档解析器"""

    def parse_word(self, file_path: str) -> List[Dict[str, Any]]:
        """解析Word文档"""
        try:
            from docx import Document
            doc = Document(file_path)
            qa_pairs = []

            # 从表格中提取
            for table_idx, table in enumerate(doc.tables):
                for row_idx, row in enumerate(table.rows):
                    if len(row.cells) >= 2:
                        question = row.cells[0].text.strip()
                        answer = row.cells[1].text.strip()

                        if (question and len(question) > 2 and
                            answer and len(answer) > 2 and
                            ('？' in question or '?' in question)):
                            qa_pairs.append({
                                'id': len(qa_pairs) + 1,
                                'question': question,
                                'answer': answer,
                                'source': os.path.basename(file_path)
                            })

            return qa_pairs
        except Exception as e:
            print(f"解析Word失败: {e}")
            return []

    def search_similar(self, query: str, qa_pairs: List[Dict[str, Any]], k: int = 3) -> List[Dict[str, Any]]:
        """搜索相似问题"""
        query_lower = query.lower()
        results = []

        for qa in qa_pairs:
            # 计算相似度
            score = 0
            q_text = qa['question'].lower()

            # 完全匹配
            if query_lower == q_text:
                score = 1.0
            # 问题包含查询词
            elif any(word in q_text for word in query_lower.split()):
                score = sum(1 for word in query_lower.split() if word in q_text) / len(query_lower.split())
            # 查询词包含在问题中
            elif any(word in query_lower for word in q_text.split()):
                score = sum(1 for word in q_text.split() if word in query_lower) / len(q_text.split())

            if score > 0:
                results.append({
                    'id': qa['id'],
                    'question': qa['question'],
                    'answer': qa['answer'],
                    'source': qa['source'],
                    'similarity': score
                })

        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:k]

def test_user_question():
    """测试用户问题"""
    print("开始验证用户问题...")

    # 1. 加载知识库
    print("\n1. 加载知识库...")
    qa_pairs = []

    # 尝试从初始化文件加载
    if os.path.exists("initialized_qa_pairs.json"):
        with open("initialized_qa_pairs.json", "r", encoding="utf-8") as f:
            qa_pairs = json.load(f)
        print(f"从文件加载了 {len(qa_pairs)} 个问答对")
    else:
        # 尝试解析QA.docx
        rag_dir = r'C:\Users\jj\Desktop\RAG'
        parser = SimpleParser()

        for file in os.listdir(rag_dir):
            if file == 'QA.docx':
                file_path = os.path.join(rag_dir, file)
                qa_pairs = parser.parse_word(file_path)
                print(f"从QA.docx解析了 {len(qa_pairs)} 个问答对")
                break

    # 2. 测试用户问题
    user_question = "为什么重置密码的邮件一直收不到?"
    print(f"\n2. 测试用户问题: {user_question}")

    if qa_pairs:
        # 搜索
        parser = SimpleParser()
        results = parser.search_similar(user_question, qa_pairs, k=3)

        print(f"\n搜索结果:")
        if results:
            for i, result in enumerate(results):
                print(f"\n{i+1}. 相似度: {result['similarity']:.2%}")
                print(f"   问题: {result['question']}")
                print(f"   答案: {result['answer']}")

                # 高亮关键词
                highlighter = SimpleHighlighter()
                keywords = highlighter.extract_keywords(user_question)
                highlighted_answer = highlighter.highlight_keywords(result['answer'], keywords[:3])

                print(f"   高亮答案: {highlighted_answer}")
        else:
            print("未找到相关结果")
    else:
        print("知识库为空")

    # 3. 生成最终回答
    print("\n3. 生成最终回答...")
    if results and results[0]['similarity'] > 0.3:
        answer = results[0]['answer']
        print(f"找到相关答案: {answer}")
    else:
        print("未找到足够相关的答案")
        print("建议联系人工客服")

    print("\n验证完成！")

if __name__ == "__main__":
    test_user_question()
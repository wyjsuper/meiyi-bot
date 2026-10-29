#!/usr/bin/env python3
"""
测试RAG功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.document_parser import DocumentParser
from utils.vector_store import VectorStore
from utils.llm_client import LLMClient
from utils.highlighter import Highlighter

def test_rag():
    """测试完整的RAG流程"""
    print("开始测试RAG功能...")

    # 1. 测试文档解析
    print("\n1. 测试文档解析...")
    parser = DocumentParser()
    rag_dir = r'C:\Users\jj\Desktop\RAG'

    # 解析目录中的Excel文件
    qa_pairs = parser.parse_directory(rag_dir)
    print(f"解析完成，共提取 {len(qa_pairs)} 个问答对")

    if qa_pairs:
        print("\n前3个问答对:")
        for i, pair in enumerate(qa_pairs[:3]):
            print(f"{i+1}. 问题: {pair['question']}")
            print(f"   答案: {pair['answer']}")
            print()

    # 2. 测试向量存储
    print("\n2. 测试向量存储...")
    vector_store = VectorStore()

    if qa_pairs:
        # 添加文档
        vector_store.add_documents(qa_pairs)
        print(f"添加 {len(qa_pairs)} 个文档到向量存储")

        # 获取文档数量
        count = vector_store.get_document_count()
        print(f"当前文档总数: {count}")

    # 3. 测试搜索功能
    print("\n3. 测试搜索功能...")
    if qa_pairs:
        # 测试搜索
        test_queries = ["报销流程", "IT资产", "合规要求"]
        for query in test_queries:
            print(f"\n搜索: {query}")
            results = vector_store.search(query, k=2)
            if results:
                for i, result in enumerate(results):
                    print(f"{i+1}. 相似度: {result['similarity']:.2%}")
                    print(f"   问题: {result['question']}")
                    print(f"   答案: {result['answer'][:100]}...")
            else:
                print("未找到相关结果")

    # 4. 测试LLM客户端（可选）
    print("\n4. 测试LLM客户端...")
    try:
        llm_client = LLMClient()

        # 测试连接
        if llm_client.test_connection():
            print("LLM连接测试成功")

            # 测试生成回答
            test_context = "问题: 报销流程是什么？\n答案: 报销流程包括填写报销单、粘贴发票、部门审批、财务审核等步骤。"
            response = llm_client.generate_response(
                prompt="报销需要多久？",
                context=test_context,
                max_tokens=100
            )
            print(f"测试回答: {response}")
        else:
            print("LLM连接测试失败")
    except Exception as e:
        print(f"LLM测试失败: {e}")

    # 5. 测试关键词高亮
    print("\n5. 测试关键词高亮...")
    highlighter = Highlighter()

    test_text = "报销流程需要填写申请表并提交相关证明文件。"
    keywords = ["报销", "申请表", "证明文件"]

    highlighted = highlighter.highlight_keywords(test_text, keywords)
    print(f"原文: {test_text}")
    print(f"高亮后: {highlighted}")

    # 测试关键词提取
    question = "如何申请IT资产报销？"
    context = "IT资产报销需要提交资产清单和采购证明。"
    extracted_keywords = highlighter.extract_keywords_from_question(question, context)
    print(f"\n问题: {question}")
    print(f"提取的关键词: {extracted_keywords}")

    print("\nRAG功能测试完成！")

if __name__ == "__main__":
    test_rag()
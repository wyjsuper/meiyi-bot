#!/usr/bin/env python3
"""
测试问答功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.document_parser import DocumentParser
from utils.vector_store import VectorStore
from utils.llm_client import LLMClient
from utils.highlighter import Highlighter

def test_qa_functionality():
    """测试问答功能"""
    print("开始测试问答功能...")

    # 1. 初始化组件
    print("\n1. 初始化组件...")
    vector_store = VectorStore()
    parser = DocumentParser()
    llm_client = LLMClient()
    highlighter = Highlighter()

    # 2. 加载知识库
    print("\n2. 加载知识库...")
    rag_dir = r'C:\Users\jj\Desktop\RAG'
    qa_pairs = []

    # 解析QA.docx
    for file in os.listdir(rag_dir):
        if file == 'QA.docx':
            file_path = os.path.join(rag_dir, file)
            qa_pairs = parser.parse_word(file_path)
            print(f"从QA.docx加载了 {len(qa_pairs)} 个问答对")
            break

    if qa_pairs:
        # 添加到向量存储
        vector_store.clear_collection()
        vector_store.add_documents(qa_pairs)
        doc_count = vector_store.get_document_count()
        print(f"向量存储中现在有 {doc_count} 个文档")

    # 3. 测试搜索
    print("\n3. 测试搜索功能...")
    test_questions = [
        "为什么重置密码的邮件一直收不到?",
        "报销流程是什么?",
        "如何申请IT资产?",
        "发票有什么要求?"
    ]

    for question in test_questions:
        print(f"\n搜索: {question}")
        results = vector_store.search(question, k=2)

        if results:
            for i, result in enumerate(results):
                print(f"{i+1}. 相似度: {result['similarity']:.2%}")
                print(f"   问题: {result['question']}")
                print(f"   答案: {result['answer'][:100]}...")
        else:
            print("未找到相关结果")

    # 4. 测试完整问答流程（不使用GLM API）
    print("\n4. 测试完整问答流程（模拟）...")

    def mock_answer_generation(question, context, keywords):
        """模拟回答生成"""
        # 在上下文中查找直接匹配的答案
        for pair in qa_pairs:
            if question.lower() in pair['question'].lower() or pair['question'].lower() in question.lower():
                return pair['answer']

        # 如果没有直接匹配，返回相关答案
        return "根据知识库信息，请参考相关文档内容。"

    for question in test_questions[:2]:  # 只测试前两个
        print(f"\n问题: {question}")

        # 搜索
        results = vector_store.search(question, k=2)

        if results:
            # 构建上下文
            context = "\n\n".join([
                f"问题: {result['question']}\n答案: {result['answer']}"
                for result in results
            ])

            # 提取关键词
            keywords = highlighter.extract_keywords_from_question(question, context)

            # 生成回答
            answer = mock_answer_generation(question, context, keywords)

            # 高亮关键词
            highlighted_answer = highlighter.highlight_keywords(answer, keywords)

            print(f"回答: {highlighted_answer}")
            print(f"参考来源: {[r['source'] for r in results]}")
        else:
            print("无法回答此问题")

    print("\n问答功能测试完成！")

if __name__ == "__main__":
    test_qa_functionality()
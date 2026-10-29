#!/usr/bin/env python3
"""
测试增强搜索功能
"""

import os
import json
from enhanced_app import EnhancedSearch, SimpleHighlighter

def test_enhanced_search():
    """测试增强搜索功能"""
    print("开始测试增强搜索功能...")

    # 1. 初始化
    search_engine = EnhancedSearch()
    highlighter = SimpleHighlighter()

    # 2. 加载知识库
    print("\n1. 加载知识库...")
    rag_dir = r'C:\Users\jj\Desktop\RAG'
    qa_pairs = []

    for file in os.listdir(rag_dir):
        if file == 'QA.docx':
            file_path = os.path.join(rag_dir, file)
            qa_pairs = search_engine.parse_word_enhanced(file_path)
            print(f"从QA.docx加载了 {len(qa_pairs)} 个问答对")
            break

    if not qa_pairs:
        print("未加载到QA数据")
        return

    # 3. 测试搜索重置密码相关问题
    print("\n2. 测试搜索重置密码相关问题...")

    user_question = "为什么重置密码的邮件一直收不到?"
    print(f"用户问题: {user_question}")

    # 使用不同阈值搜索
    thresholds = [0.3, 0.1, 0.0]
    for threshold in thresholds:
        print(f"\n使用相似度阈值 >= {threshold}:")
        results = search_engine.search_multiple_answers(user_question, qa_pairs, max_answers=10)

        filtered_results = [r for r in results if r['similarity'] >= threshold]
        print(f"找到 {len(filtered_results)} 个答案:")

        for i, result in enumerate(filtered_results[:5], 1):
            print(f"\n{i}. [相似度: {result['similarity']:.2%}] [位置: {result['index']}]")
            print(f"   问题: {result['question']}")
            print(f"   答案: {result['answer']}")

    # 4. 显示所有密码相关的答案
    print(f"\n3. 显示所有密码相关的答案:")
    password_keywords = ['密码', '重置', '登录', '账号', '账户', '验证', '邮箱']

    password_related = []
    for qa in qa_pairs:
        q_lower = qa['question'].lower()
        a_lower = qa['answer'].lower()

        if any(keyword in q_lower or keyword in a_lower for keyword in password_keywords):
            password_related.append(qa)

    print(f"共找到 {len(password_related)} 个密码相关的问答:")
    for i, qa in enumerate(password_related[:10], 1):
        print(f"\n{i}. [位置: {qa['index']}]")
        print(f"   问题: {qa['question']}")
        print(f"   答案: {qa['answer']}")

    # 5. 测试关键词高亮
    print(f"\n4. 测试关键词高亮...")
    test_answer = "1，重置密码页面请输入完整公司邮箱"
    keywords = highlighter.extract_keywords(user_question)

    highlighted = highlighter.highlight_keywords(test_answer, keywords)
    print(f"原文: {test_answer}")
    print(f"高亮: {highlighted}")

    # 6. 生成完整回答
    print(f"\n5. 生成完整回答...")
    results = search_engine.search_multiple_answers(user_question, qa_pairs, max_answers=5)

    if results:
        answer_parts = []
        answer_parts.append("### 🎯 高相关答案")

        for i, result in enumerate(results[:3], 1):
            answer_parts.append(f"**答案{i}**（相似度: {result['similarity']:.2%}）：\n{result['answer']}")

        answer = "\n\n".join(answer_parts)
        highlighted_answer = highlighter.highlight_keywords(answer, keywords)

        print(f"完整回答:\n{highlighted_answer}")

    print("\n增强搜索功能测试完成！")

if __name__ == "__main__":
    test_enhanced_search()
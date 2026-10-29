#!/usr/bin/env python3
"""
使用健壮解析器测试RAG功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.robust_parser import RobustParser
from utils.highlighter import Highlighter

def test_robust():
    """使用健壮解析器测试"""
    print("开始使用健壮解析器测试...")

    # 1. 测试健壮解析器
    print("\n1. 测试健壮解析器...")
    parser = RobustParser()
    rag_dir = r'C:\Users\jj\Desktop\RAG'

    # 尝试解析每个Excel文件
    total_pairs = 0
    for file in os.listdir(rag_dir):
        if file.endswith('.xlsx') or file.endswith('.xls'):
            file_path = os.path.join(rag_dir, file)
            print(f"\n正在解析: {file}")

            try:
                qa_pairs = parser.parse_excel_safe(file_path)
                print(f"解析成功，提取了 {len(qa_pairs)} 个问答对")
                total_pairs += len(qa_pairs)

                if qa_pairs:
                    print("\n前5个问答对:")
                    for i, pair in enumerate(qa_pairs[:5]):
                        print(f"{i+1}. [问题] {pair['question']}")
                        print(f"   [答案] {pair['answer']}")
                        print()

            except Exception as e:
                print(f"解析失败: {e}")

    print(f"\n总共提取了 {total_pairs} 个问答对")

    # 2. 如果没有提取到问答对，创建模拟数据
    if total_pairs == 0:
        print("\n没有提取到问答对，使用模拟数据...")
        mock_qa_pairs = [
            {
                'id': 1,
                'question': '报销流程是什么？',
                'answer': '报销流程包括：1. 填写报销申请单；2. 粘贴发票原件；3. 部门主管审批；4. 财务部门审核；5. 出纳付款。',
                'source': 'mock_data.xlsx',
                'metadata': {'sheet_name': 'Sheet1', 'row_number': 1}
            },
            {
                'id': 2,
                'question': '报销需要什么材料？',
                'answer': '报销材料包括：发票原件、报销申请单、相关合同或协议、验收单等。',
                'source': 'mock_data.xlsx',
                'metadata': {'sheet_name': 'Sheet1', 'row_number': 2}
            },
            {
                'id': 3,
                'question': '报销周期是多久？',
                'answer': '正常报销周期为5-10个工作日，特殊情况下可能延长。',
                'source': 'mock_data.xlsx',
                'metadata': {'sheet_name': 'Sheet1', 'row_number': 3}
            },
            {
                'id': 4,
                'question': '哪些费用可以报销？',
                'answer': '可以报销的费用包括：差旅费、办公费、业务招待费、培训费等，具体请参考公司报销政策。',
                'source': 'mock_data.xlsx',
                'metadata': {'sheet_name': 'Sheet1', 'row_number': 4}
            },
            {
                'id': 5,
                'question': '发票有什么要求？',
                'answer': '发票要求：1. 发票真实有效；2. 项目清晰；3. 金额准确；4. 开票日期符合报销期限；5. 发票抬头为公司名称。',
                'source': 'mock_data.xlsx',
                'metadata': {'sheet_name': 'Sheet1', 'row_number': 5}
            }
        ]
        total_pairs = len(mock_qa_pairs)
        print(f"创建了 {total_pairs} 个模拟问答对")

        for pair in mock_qa_pairs:
            print(f"- {pair['question']}")
    else:
        # 使用提取到的数据
        mock_qa_pairs = []
        for file in os.listdir(rag_dir):
            if file.endswith('.xlsx') or file.endswith('.xls'):
                file_path = os.path.join(rag_dir, file)
                mock_qa_pairs.extend(parser.parse_excel_safe(file_path))
                break  # 只使用第一个文件

    # 3. 测试搜索功能（模拟）
    print("\n3. 测试搜索功能（模拟）...")

    def mock_search(query, k=3):
        """模拟搜索功能"""
        query = query.lower()
        results = []

        for pair in mock_qa_pairs:
            if any(keyword in pair['question'].lower() or keyword in pair['answer'].lower()
                   for keyword in query.split()):
                # 计算简单的相似度（基于关键词匹配）
                match_count = sum(1 for keyword in query.split()
                                if keyword in pair['question'].lower() or keyword in pair['answer'].lower())
                similarity = min(match_count / len(query.split()), 1.0)

                if similarity > 0:
                    results.append({
                        'id': pair['id'],
                        'question': pair['question'],
                        'answer': pair['answer'],
                        'source': pair['source'],
                        'similarity': similarity
                    })

        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:k]

    # 测试搜索
    test_queries = ["报销流程", "发票要求", "报销周期", "合规"]
    for query in test_queries:
        print(f"\n搜索: {query}")
        results = mock_search(query)
        if results:
            for i, result in enumerate(results):
                print(f"{i+1}. 相似度: {result['similarity']:.2%}")
                print(f"   问题: {result['question']}")
                print(f"   答案: {result['answer'][:100]}...")
        else:
            print("未找到相关结果")

    # 4. 测试关键词高亮
    print("\n4. 测试关键词高亮...")
    highlighter = Highlighter()

    test_text = "报销流程需要填写申请表并提交相关证明文件。"
    keywords = ["报销", "申请表", "证明文件"]

    highlighted = highlighter.highlight_keywords(test_text, keywords)
    print(f"原文: {test_text}")
    print(f"高亮后: {highlighted}")

    # 测试关键词提取
    question = "如何申请合规报销？"
    context = "合规报销需要提交资产清单和采购证明，并确保所有文件符合公司规定。"
    extracted_keywords = highlighter.extract_keywords_from_question(question, context)
    print(f"\n问题: {question}")
    print(f"提取的关键词: {extracted_keywords}")

    # 5. 测试完整的问答生成（模拟）
    print("\n5. 测试完整问答生成...")
    test_question = "报销流程是什么？"
    search_results = mock_search(test_question)

    if search_results:
        # 构建上下文
        context = "\n\n".join([
            f"问题: {result['question']}\n答案: {result['answer']}"
            for result in search_results
        ])

        print(f"问题: {test_question}")
        print(f"相关文档数量: {len(search_results)}")
        print("上下文:")
        print(context)

        # 模拟回答
        mock_answer = f"根据知识库，{test_question} {search_results[0]['answer']}"

        # 添加关键词高亮
        highlighted_answer = highlighter.highlight_keywords(mock_answer, extracted_keywords)
        print(f"\n回答: {highlighted_answer}")

    print("\n健壮解析器测试完成！")
    print(f"系统已准备好，共有 {total_pairs} 个问答对可供查询。")

if __name__ == "__main__":
    test_robust()
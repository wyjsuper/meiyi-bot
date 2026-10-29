#!/usr/bin/env python3
"""
简化版RAG测试
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.document_parser import DocumentParser
from utils.highlighter import Highlighter

def test_simple():
    """测试简化的RAG功能"""
    print("开始测试简化版RAG功能...")

    # 1. 测试文档解析
    print("\n1. 测试文档解析...")
    parser = DocumentParser()
    rag_dir = r'C:\Users\jj\Desktop\RAG'

    # 列出文件
    print("目录中的文件:")
    for file in os.listdir(rag_dir):
        print(f"  - {file}")

    # 尝试解析Excel文件
    for file in os.listdir(rag_dir):
        if file.endswith('.xlsx') or file.endswith('.xls'):
            file_path = os.path.join(rag_dir, file)
            print(f"\n正在解析: {file}")
            try:
                qa_pairs = parser.parse_excel(file_path)
                print(f"解析成功，共提取 {len(qa_pairs)} 个问答对")

                if qa_pairs:
                    print("\n前3个问答对:")
                    for i, pair in enumerate(qa_pairs[:3]):
                        print(f"{i+1}. 问题: {pair['question']}")
                        print(f"   答案: {pair['answer']}")
                        print()
                break
            except Exception as e:
                print(f"解析失败: {e}")
                # 尝试使用不同的编码方式
                try:
                    print("尝试使用不同的方法解析...")
                    # 这里可以添加其他解析方法
                except:
                    pass

    # 2. 测试关键词高亮
    print("\n2. 测试关键词高亮...")
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

    # 3. 创建模拟的问答对
    print("\n3. 创建模拟问答数据...")
    mock_qa_pairs = [
        {
            'id': 1,
            'question': '报销流程是什么？',
            'answer': '报销流程包括：1. 填写报销申请单；2. 粘贴发票原件；3. 部门主管审批；4. 财务部门审核；5. 出纳付款。',
            'source': 'mock_data.xlsx'
        },
        {
            'id': 2,
            'question': '报销需要什么材料？',
            'answer': '报销材料包括：发票原件、报销申请单、相关合同或协议、验收单等。',
            'source': 'mock_data.xlsx'
        },
        {
            'id': 3,
            'question': '报销周期是多久？',
            'answer': '正常报销周期为5-10个工作日，特殊情况下可能延长。',
            'source': 'mock_data.xlsx'
        }
    ]

    print(f"创建了 {len(mock_qa_pairs)} 个模拟问答对")
    for pair in mock_qa_pairs:
        print(f"- {pair['question']}")

    print("\n简化版RAG功能测试完成！")

if __name__ == "__main__":
    test_simple()
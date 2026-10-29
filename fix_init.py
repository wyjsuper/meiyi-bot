#!/usr/bin/env python3
"""
修复应用初始化问题
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.document_parser import DocumentParser
from utils.robust_parser import RobustParser

def initialize_knowledge_base():
    """初始化知识库"""
    print("正在初始化知识库...")

    # 解析器
    parser = DocumentParser()
    robust_parser = RobustParser()
    rag_dir = r'C:\Users\jj\Desktop\RAG'

    # 首先检查是否存在QA.docx
    qa_pairs = []

    # 解析Word文档
    for file in os.listdir(rag_dir):
        if file == 'QA.docx':
            file_path = os.path.join(rag_dir, file)
            print(f"解析Word文档: {file}")
            try:
                qa_pairs = parser.parse_word(file_path)
                print(f"从Word提取了 {len(qa_pairs)} 个问答对")
                break
            except Exception as e:
                print(f"Word解析失败: {e}")

    # 如果Word文档解析失败或为空，尝试解析Excel
    if not qa_pairs:
        print("Word文档为空或解析失败，尝试解析Excel...")
        for file in os.listdir(rag_dir):
            if file.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(rag_dir, file)
                try:
                    qa_pairs = parser.parse_excel(file_path)
                    print(f"从Excel提取了 {len(qa_pairs)} 个问答对")
                    break
                except Exception as e:
                    print(f"Excel解析失败: {e}")

    # 如果还是为空，使用模拟数据
    if not qa_pairs:
        print("没有解析到数据，使用模拟数据...")
        qa_pairs = [
            {
                'id': 1,
                'question': '为什么重置密码的邮件一直收不到?',
                'answer': '如果重置密码的邮件收不到，请检查：1. 垃圾邮件箱；2. 邮箱地址是否正确；3. 网络连接是否正常；4. 联系IT部门协助。',
                'source': 'mock_data.xlsx'
            }
        ]

    # 保存解析结果到文件
    import json
    with open("initialized_qa_pairs.json", "w", encoding="utf-8") as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)

    print(f"知识库初始化完成，共 {len(qa_pairs)} 个问答对")
    return qa_pairs

if __name__ == "__main__":
    initialize_knowledge_base()
#!/usr/bin/env python3
"""
测试Word文档解析
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.document_parser import DocumentParser

def test_word_parsing():
    """测试Word文档解析"""
    print("开始测试Word文档解析...")

    parser = DocumentParser()
    rag_dir = r'C:\Users\jj\Desktop\RAG'

    # 测试Word文档
    for file in os.listdir(rag_dir):
        if file.endswith('.docx'):
            file_path = os.path.join(rag_dir, file)
            print(f"\n正在解析Word文档: {file}")

            try:
                qa_pairs = parser.parse_word(file_path)
                print(f"解析成功，提取了 {len(qa_pairs)} 个问答对")

                if qa_pairs:
                    print("\n前5个问答对:")
                    for i, pair in enumerate(qa_pairs[:5]):
                        print(f"{i+1}. [问题] {pair['question']}")
                        print(f"   [答案] {pair['answer']}")
                        print()

            except Exception as e:
                print(f"解析失败: {e}")

    print("\n测试完成！")

if __name__ == "__main__":
    test_word_parsing()
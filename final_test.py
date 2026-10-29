#!/usr/bin/env python3
"""
完整功能测试
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.document_parser import DocumentParser
from utils.robust_parser import RobustParser

def test_complete_functionality():
    """测试完整功能"""
    print("开始完整功能测试...")
    print("=" * 50)

    # 初始化解析器
    parser = DocumentParser()
    robust_parser = RobustParser()
    rag_dir = r'C:\Users\jj\Desktop\RAG'

    total_pairs = 0

    # 1. 测试Excel文件
    print("\n1. 测试Excel文件解析...")
    for file in os.listdir(rag_dir):
        if file.endswith(('.xlsx', '.xls')):
            file_path = os.path.join(rag_dir, file)
            print(f"\n解析Excel: {file}")

            try:
                # 使用普通解析器
                qa_pairs = parser.parse_excel(file_path)
                print(f"普通解析器: {len(qa_pairs)} 个问答对")

                # 使用健壮解析器
                robust_pairs = robust_parser.parse_excel_safe(file_path)
                print(f"健壮解析器: {len(robust_pairs)} 个问答对")

                # 使用数量较多的结果
                if len(robust_pairs) > len(qa_pairs):
                    total_pairs += len(robust_pairs)
                    print("使用健壮解析器结果")
                else:
                    total_pairs += len(qa_pairs)
                    print("使用普通解析器结果")

            except Exception as e:
                print(f"Excel解析失败: {e}")

    # 2. 测试Word文件
    print("\n2. 测试Word文件解析...")
    for file in os.listdir(rag_dir):
        if file.endswith('.docx'):
            file_path = os.path.join(rag_dir, file)
            print(f"\n解析Word: {file}")

            try:
                # 使用文档解析器
                qa_pairs = parser.parse_word(file_path)
                print(f"文档解析器: {len(qa_pairs)} 个问答对")
                total_pairs += len(qa_pairs)

            except Exception as e:
                print(f"Word解析失败: {e}")

    # 3. 测试目录解析
    print("\n3. 测试目录批量解析...")
    try:
        # 使用普通解析器解析目录
        directory_pairs = parser.parse_directory(rag_dir)
        print(f"目录解析结果: {len(directory_pairs)} 个问答对")

        # 使用健壮解析器解析每个文件
        robust_directory_pairs = []
        for file in os.listdir(rag_dir):
            if file.endswith(('.xlsx', '.xls', '.docx')):
                file_path = os.path.join(rag_dir, file)
                if file.endswith('.xlsx') or file.endswith('.xls'):
                    pairs = robust_parser.parse_excel_safe(file_path)
                else:
                    pairs = parser.parse_word(file_path)
                robust_directory_pairs.extend(pairs)

        print(f"健壮解析器目录结果: {len(robust_directory_pairs)} 个问答对")

        # 选择较好的结果
        if len(robust_directory_pairs) > len(directory_pairs):
            total_pairs = len(robust_directory_pairs)
            final_pairs = robust_directory_pairs
            print("使用健壮解析器结果")
        else:
            total_pairs = len(directory_pairs)
            final_pairs = directory_pairs
            print("使用普通解析器结果")

    except Exception as e:
        print(f"目录解析失败: {e}")

    # 4. 显示最终结果
    print("\n" + "=" * 50)
    print("最终统计:")
    print(f"总共提取了 {total_pairs} 个问答对")

    if final_pairs:
        print("\n前10个问答对:")
        for i, pair in enumerate(final_pairs[:10]):
            print(f"{i+1}. [{pair['source']}] {pair['question']}")
            if pair['answer']:
                print(f"   答案: {pair['answer'][:100]}...")
            print()

        # 显示来源统计
        sources = {}
        for pair in final_pairs:
            source = pair['source']
            sources[source] = sources.get(source, 0) + 1

        print("\n来源统计:")
        for source, count in sources.items():
            print(f"- {source}: {count} 个问答对")

    print("\n测试完成！")
    return final_pairs

if __name__ == "__main__":
    qa_pairs = test_complete_functionality()

    # 保存结果
    if qa_pairs:
        import json
        with open("qa_pairs_result.json", "w", encoding="utf-8") as f:
            json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到 qa_pairs_result.json")
#!/usr/bin/env python3
"""
优化搜索规则，确保显示所有相关答案
"""

import os
import json
import re
from typing import List, Dict, Any

class OptimizedSearch:
    """优化的搜索类"""

    def __init__(self):
        pass

    def parse_qa_from_docx(self, file_path: str) -> List[Dict[str, Any]]:
        """从Word文档解析QA对，优化版本"""
        try:
            from docx import Document
            doc = Document(file_path)
            qa_pairs = []

            # 方法1: 从表格提取
            for table_idx, table in enumerate(doc.tables):
                for row_idx, row in enumerate(table.rows):
                    if len(row.cells) >= 2:
                        question = row.cells[0].text.strip()
                        answer = row.cells[1].text.strip()

                        if (question and len(question) > 2 and
                            answer and len(answer) > 2 and
                            ('？' in question or '?' in question or '为什么' in question or '如何' in question or '怎么' in question)):
                            qa_pairs.append({
                                'id': len(qa_pairs) + 1,
                                'question': question,
                                'answer': answer,
                                'source': os.path.basename(file_path),
                                'table_idx': table_idx,
                                'row_idx': row_idx
                            })

            print(f"从表格提取了 {len(qa_pairs)} 个QA对")
            return qa_pairs

        except Exception as e:
            print(f"解析失败: {e}")
            return []

    def enhanced_search(self, query: str, qa_pairs: List[Dict[str, Any]], threshold: float = 0.1) -> List[Dict[str, Any]]:
        """增强的搜索算法"""
        query_lower = query.lower()
        results = []

        for qa in qa_pairs:
            score = 0
            q_text = qa['question'].lower()
            a_text = qa['answer'].lower()

            # 1. 完全匹配问题 (最高分)
            if query_lower == q_text:
                score = 1.0
            # 2. 问题关键词匹配
            elif any(word in q_text for word in query_lower.split()):
                score = sum(1 for word in query_lower.split() if word in q_text) / len(query_lower.split())
            # 3. 查询词包含在问题中
            elif query_lower in q_text:
                score = 0.8
            # 4. 答案包含查询词
            elif query_lower in a_text:
                score = 0.5
            # 5. 部分匹配
            else:
                # 计算共同词汇
                query_words = set(query_lower.split())
                q_words = set(q_text.split())
                a_words = set(a_text.split())

                # 问题中的共同词
                q_overlap = len(query_words & q_words)
                # 答案中的共同词
                a_overlap = len(query_words & a_words)

                if q_overlap > 0 or a_overlap > 0:
                    score = (q_overlap + a_overlap * 0.5) / len(query_words)

            if score >= threshold:
                results.append({
                    'id': qa['id'],
                    'question': qa['question'],
                    'answer': qa['answer'],
                    'source': qa['source'],
                    'similarity': score,
                    'match_type': self._get_match_type(query_lower, q_text, a_text)
                })

        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results

    def _get_match_type(self, query: str, question: str, answer: str) -> str:
        """获取匹配类型"""
        if query == question:
            return "完全匹配"
        elif any(word in question for word in query.split()):
            return "关键词匹配"
        elif query in question:
            return "问题包含"
        elif query in answer:
            return "答案包含"
        else:
            return "部分匹配"

def test_optimized_search():
    """测试优化后的搜索"""
    print("开始测试优化后的搜索...")

    # 1. 加载知识库
    print("\n1. 加载知识库...")
    qa_pairs = []

    # 尝试解析QA.docx
    rag_dir = r'C:\Users\jj\Desktop\RAG'
    search_engine = OptimizedSearch()

    for file in os.listdir(rag_dir):
        if file == 'QA.docx':
            file_path = os.path.join(rag_dir, file)
            qa_pairs = search_engine.parse_qa_from_docx(file_path)
            break

    if not qa_pairs:
        print("未找到QA数据")
        return

    print(f"加载了 {len(qa_pairs)} 个QA对")

    # 2. 搜索重置密码相关的问题
    print("\n2. 搜索重置密码相关的问题...")
    query = "重置密码"
    results = search_engine.enhanced_search(query, qa_pairs, threshold=0.1)

    print(f"\n找到 {len(results)} 个相关结果:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. [相似度: {result['similarity']:.2%}] [{result['match_type']}]")
        print(f"   问题: {result['question']}")
        print(f"   答案: {result['answer']}")

    # 3. 搜索用户具体的问题
    print("\n3. 搜索用户具体问题...")
    user_query = "为什么重置密码的邮件一直收不到?"
    user_results = search_engine.enhanced_search(user_query, qa_pairs, threshold=0.1)

    print(f"\n用户问题: {user_query}")
    print(f"找到 {len(user_results)} 个相关结果:")
    for i, result in enumerate(user_results, 1):
        print(f"\n{i}. [相似度: {result['similarity']:.2%}] [{result['match_type']}]")
        print(f"   问题: {result['question']}")
        print(f"   答案: {result['answer']}")

    # 4. 显示所有相关答案（不管相似度，只要相关）
    print("\n4. 显示所有可能相关的答案...")

    # 查找所有包含"重置密码"的问答
    password_reset_qas = []
    for qa in qa_pairs:
        if ('重置密码' in qa['question'] or '重置密码' in qa['answer'] or
            '密码' in qa['question'] or '密码' in qa['answer']):
            password_reset_qas.append(qa)

    print(f"\n所有密码相关的问答（共 {len(password_reset_qas)} 条）:")
    for i, qa in enumerate(password_reset_qas, 1):
        print(f"\n{i}. [{qa['source']}]")
        print(f"   问题: {qa['question']}")
        print(f"   答案: {qa['answer']}")

if __name__ == "__main__":
    test_optimized_search()
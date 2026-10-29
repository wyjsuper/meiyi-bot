#!/usr/bin/env python3
"""
优化搜索算法，减少误匹配
"""

import os
import json
import re
from typing import List, Dict, Any, Tuple
from collections import Counter

class OptimizedSearchEngine:
    """优化的搜索引擎"""

    def __init__(self):
        # 定义高权重关键词
        self.high_weight_keywords = {
            '密码': ['密码', '重置密码', '找回密码', '修改密码', '重置口令'],
            '邮箱': ['邮箱', '电子邮箱', 'email', '邮件地址'],
            '登录': ['登录', '登入', 'signin', 'log in', '账号'],
            '收不到': ['收不到', '未收到', '没有收到', '没收到', '无法接收'],
            '验证': ['验证', '验证码', '验证邮件', '短信验证']
        }

        # 定义低权重关键词（会降低匹配度）
        self.low_weight_keywords = {
            '下载': ['下载', 'download', '安装', 'app', '应用市场'],
            '三星': ['三星', 'samsung', 'galaxy'],
            '云简业财': ['云简业财', 'cloudpense']
        }

    def parse_qa_pairs(self, file_path: str) -> List[Dict[str, Any]]:
        """解析QA对"""
        try:
            from docx import Document
            doc = Document(file_path)
            qa_pairs = []

            for i in range(len(doc.paragraphs) - 1):
                para1 = doc.paragraphs[i]
                para2 = doc.paragraphs[i + 1]

                text1 = para1.text.strip()
                text2 = para2.text.strip()

                if text1 and ('？' in text1 or '?' in text1) and len(text1) > 5:
                    if text2 and len(text2) > 5:
                        qa_pairs.append({
                            'id': len(qa_pairs) + 1,
                            'question': text1,
                            'answer': text2,
                            'index': i + 1
                        })

            return qa_pairs
        except Exception as e:
            print(f"解析失败: {e}")
            return []

    def calculate_weighted_score(self, query: str, qa: Dict[str, Any]) -> float:
        """计算加权相似度分数"""
        query_lower = query.lower()
        question_lower = qa['question'].lower()
        answer_lower = qa['answer'].lower()

        # 基础分数
        score = 0.0

        # 1. 完全匹配问题 - 最高分
        if query_lower == question_lower:
            return 1.0

        # 2. 检查高权重关键词
        high_score = 0.0
        high_weight_count = 0

        for category, keywords in self.high_weight_keywords.items():
            category_found = False
            for keyword in keywords:
                if keyword in query_lower:
                    # 检查关键词是否在问题或答案中
                    if keyword in question_lower:
                        high_score += 1.0
                    elif keyword in answer_lower:
                        high_score += 0.8
                    category_found = True

            if category_found:
                high_weight_count += 1

        # 3. 检查低权重关键词 - 会降低分数
        low_penalty = 0.0
        for category, keywords in self.low_weight_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    # 如果问题中包含低权重关键词，但答案不相关，则降低分数
                    if keyword in question_lower and ('密码' not in question_lower and
                                                   '邮箱' not in question_lower and
                                                   '登录' not in question_lower):
                        low_penalty += 0.3

        # 4. 关键词匹配
        query_words = set(query_lower.split())
        q_words = set(question_lower.split())
        a_words = set(answer_lower.split())

        # 问题中的共同词
        q_overlap = len(query_words & q_words)
        # 答案中的共同词
        a_overlap = len(query_words & a_words)

        keyword_score = 0.0
        if len(query_words) > 0:
            # 问题关键词匹配权重更高
            keyword_score = (q_overlap * 0.7 + a_overlap * 0.3) / len(query_words)

        # 计算总分
        # 高权重分数很重要，但要有惩罚机制
        if high_score > 0 and high_weight_count >= 2:  # 至少2个高权重类别
            score = min(high_score * 0.4, 1.0)  # 高权重最多占40%

        # 加上关键词分数
        score += keyword_score * 0.4

        # 减去低权重惩罚
        score -= low_penalty

        # 确保分数在0-1之间
        return max(0.0, min(1.0, score))

    def search_with_penalty(self, query: str, qa_pairs: List[Dict[str, Any]],
                          max_results: int = 10, min_score: float = 0.2) -> List[Dict[str, Any]]:
        """带惩罚机制的搜索"""
        results = []

        for qa in qa_pairs:
            score = self.calculate_weighted_score(query, qa)

            if score >= min_score:
                results.append({
                    'id': qa['id'],
                    'question': qa['question'],
                    'answer': qa['answer'],
                    'similarity': score,
                    'index': qa['index']
                })

        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:max_results]

    def analyze_query_categories(self, query: str) -> List[str]:
        """分析查询的类别"""
        categories = []

        for category, keywords in self.high_weight_keywords.items():
            for keyword in keywords:
                if keyword in query.lower():
                    categories.append(category)
                    break

        return categories

def test_optimized_search():
    """测试优化后的搜索"""
    print("开始测试优化后的搜索算法...")

    # 1. 初始化
    search_engine = OptimizedSearchEngine()

    # 2. 加载知识库
    rag_dir = r'C:\Users\jj\Desktop\RAG'
    qa_pairs = []

    for file in os.listdir(rag_dir):
        if file == 'QA.docx':
            file_path = os.path.join(rag_dir, file)
            qa_pairs = search_engine.parse_qa_pairs(file_path)
            print(f"加载了 {len(qa_pairs)} 个QA对")
            break

    if not qa_pairs:
        print("未加载到QA数据")
        return

    # 3. 测试用户问题
    test_queries = [
        "为什么重置密码的邮件一直收不到?",
        "云简业财app在应用市场搜不到怎么办?",
        "安卓应用市场搜不到云简业财app怎么办?",
        "部分三星的应用市场没有上架，可通过该链接下载"
    ]

    for query in test_queries:
        print(f"\n" + "="*50)
        print(f"测试查询: {query}")
        print("="*50)

        # 分析查询类别
        categories = search_engine.analyze_query_categories(query)
        print(f"查询类别: {categories}")

        # 使用优化搜索
        results = search_engine.search_with_penalty(query, qa_pairs, max_results=5)

        print(f"\n搜索结果:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. [相似度: {result['similarity']:.2%}]")
            print(f"   问题: {result['question']}")
            print(f"   答案: {result['answer']}")

            # 分析匹配原因
            score = search_engine.calculate_weighted_score(query, result)
            print(f"   分析分数: {score:.3f}")

        # 对比使用普通搜索
        print(f"\n" + "-"*30)
        print("普通搜索对比:")

        def simple_search(query, qa_pairs):
            query_lower = query.lower()
            results = []
            for qa in qa_pairs:
                if query_lower in qa['question'].lower() or query_lower in qa['answer'].lower():
                    results.append({
                        'question': qa['question'],
                        'answer': qa['answer']
                    })
            return results

        simple_results = simple_search(query, qa_pairs)
        for i, result in enumerate(simple_results[:3], 1):
            print(f"{i}. {result['question']}")

    # 4. 验证修复效果
    print(f"\n" + "="*50)
    print("验证问题修复效果:")
    print("="*50)

    problem_query = "安卓应用市场搜不到云简业财app怎么办?"
    print(f"问题: {problem_query}")

    results = search_engine.search_with_penalty(problem_query, qa_pairs, max_results=5)

    print(f"\n优化后结果:")
    found_app_related = False
    for result in results:
        if 'app' in result['answer'].lower() or '下载' in result['answer'].lower():
            found_app_related = True
            break

    if found_app_related:
        print("✅ 仍然存在误匹配问题")

        # 进一步优化
        print("\n实施进一步优化...")

        def further_optimized_search(query, qa_pairs):
            """进一步优化的搜索"""
            query_lower = query.lower()
            results = []

            # 如果查询包含app/应用市场/下载等词
            app_keywords = ['app', '应用市场', '下载', '安装']
            has_app_keyword = any(keyword in query_lower for keyword in app_keywords)

            for qa in qa_pairs:
                question_lower = qa['question'].lower()
                answer_lower = qa['answer'].lower()

                score = 0.0

                # 如果是关于app的查询
                if has_app_keyword:
                    # 只匹配包含app相关的问题
                    if any(keyword in question_lower for keyword in app_keywords):
                        # 计算匹配度
                        if query_lower == question_lower:
                            score = 1.0
                        elif any(word in question_lower for word in query_lower.split()):
                            score = sum(1 for word in query_lower.split() if word in question_lower) / len(query_lower.split())

                        if score > 0:
                            results.append({
                                'question': qa['question'],
                                'answer': qa['answer'],
                                'similarity': score
                            })
                else:
                    # 原有的密码相关搜索逻辑
                    if '密码' in query_lower or '邮箱' in query_lower:
                        if '密码' in question_lower or '邮箱' in question_lower:
                            score = 1.0 if query_lower == question_lower else 0.8

                            if score > 0:
                                results.append({
                                    'question': qa['question'],
                                    'answer': qa['answer'],
                                    'similarity': score
                                })

            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results

        optimized_results = further_optimized_search(problem_query, qa_pairs)
        print(f"\n进一步优化后结果:")
        for i, result in enumerate(optimized_results[:5], 1):
            print(f"{i}. [相似度: {result['similarity']:.2%}]")
            print(f"   {result['question']}")

if __name__ == "__main__":
    test_optimized_search()
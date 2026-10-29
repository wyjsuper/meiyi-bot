import re
from typing import List, Dict, Any

class Highlighter:
    """关键词高亮处理器"""

    def __init__(self):
        pass

    def highlight_keywords(self, text: str, keywords: List[str],
                         highlight_tag: str = 'mark',
                         color: str = '#ffff00') -> str:
        """
        高亮文本中的关键词

        Args:
            text: 原始文本
            keywords: 关键词列表
            highlight_tag: 高亮标签（mark/em/strong等）
            color: 高亮颜色

        Returns:
            高亮后的HTML文本
        """
        if not keywords:
            return text

        # 转义正则表达式特殊字符
        escaped_keywords = [re.escape(keyword) for keyword in keywords if keyword]

        if not escaped_keywords:
            return text

        # 创建正则表达式
        pattern = '|'.join(escaped_keywords)

        # 替换匹配的关键词
        def replace_match(match):
            word = match.group()
            if highlight_tag == 'mark':
                return f'<mark style="background-color: {color}; padding: 2px 4px; border-radius: 3px;">{word}</mark>'
            elif highlight_tag == 'em':
                return f'<em style="color: {color}; font-weight: bold;">{word}</em>'
            elif highlight_tag == 'strong':
                return f'<strong style="color: {color};">{word}</strong>'
            else:
                return f'<{highlight_tag} style="background-color: {color};">{word}</{highlight_tag}>'

        # 执行替换
        highlighted_text = re.sub(pattern, replace_match, text, flags=re.IGNORECASE)

        return highlighted_text

    def extract_keywords_from_question(self, question: str, context: str = "") -> List[str]:
        """
        从问题和上下文中提取关键词

        Args:
            question: 用户问题
            context: 上下文信息

        Returns:
            关键词列表
        """
        # 简单的关键词提取策略
        # 可以根据需要使用更复杂的NLP方法

        # 合并问题和上下文
        full_text = f"{question} {context}"

        # 移除停用词
        stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'
        }

        # 简单分词（按标点符号和空格）
        words = re.findall(r'[一-鿿]+|[a-zA-Z]+', full_text)

        # 过滤停用词和短词
        keywords = []
        for word in words:
            if (len(word) >= 2 and
                word not in stopwords and
                not word.isdigit() and
                word not in keywords):
                keywords.append(word)

        return keywords[:5]  # 返回前5个关键词

    def format_response_with_references(self,
                                     response: str,
                                     sources: List[Dict[str, Any]],
                                     keywords: List[str] = None) -> str:
        """
        格式化回答，添加引用和高亮

        Args:
            response: AI回答
            sources: 引用的知识库来源
            keywords: 关键词列表

        Returns:
            格式化后的HTML回答
        """
        if keywords:
            # 高亮回答中的关键词
            response = self.highlight_keywords(response, keywords)

        # 添加引用信息
        if sources:
            references_html = """
            <div style="margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 5px;">
                <h4 style="margin: 0 0 10px 0; color: #333;">📚 参考来源：</h4>
            """

            for i, source in enumerate(sources[:3], 1):
                references_html += f"""
                <div style="margin: 10px 0; padding: 10px; background: white; border-left: 3px solid #007bff; border-radius: 3px;">
                    <strong>来源 {i}:</strong> {source.get('source', '未知')}<br>
                    <strong>相似度:</strong> {source.get('similarity', 0):.2%}<br>
                    <strong>问题:</strong> {source.get('question', '')[:100]}...
                </div>
                """

            references_html += "</div>"
            response += references_html

        return response
import os
import openpyxl
from typing import List, Dict, Any, Optional
import json
import logging
from docx import Document

class DocumentParser:
    """文档解析器，用于处理Excel和Word文件中的问答数据"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_excel(self, file_path: str, sheet_name: str = None, header_row: int = 1) -> List[Dict[str, Any]]:
        """
        解析Excel文件，提取问答对

        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称（可选）
            header_row: 表头所在行（从1开始）

        Returns:
            包含问答对的字典列表
        """
        try:
            # 加载工作簿
            workbook = openpyxl.load_workbook(file_path, data_only=True)

            # 选择工作表
            if sheet_name:
                sheet = workbook[sheet_name]
            else:
                sheet = workbook.active

            # 获取表头
            headers = []
            for col in sheet.iter_rows(min_row=header_row, max_row=header_row, values_only=True):
                headers = list(col)
                break

            # 提取数据
            qa_pairs = []
            for row_idx, row in enumerate(sheet.iter_rows(min_row=header_row + 1, values_only=True), start=header_row + 1):
                if len(row) >= len(headers) and row[0] and str(row[0]).strip():
                    # 处理每一行数据
                    row_data = {}
                    for i, header in enumerate(headers):
                        if header and str(header).strip():
                            row_data[str(header).strip()] = str(row[i]) if row[i] else ""

                    # 检查是否包含问题或答案
                    if '问题' in row_data or 'question' in row_data or 'q' in row_data:
                        qa_pairs.append({
                            'id': len(qa_pairs) + 1,
                            'question': row_data.get('问题', row_data.get('question', row_data.get('q', ''))),
                            'answer': row_data.get('答案', row_data.get('answer', row_data.get('a', ''))),
                            'source': os.path.basename(file_path),
                            'metadata': {
                                'sheet_name': sheet.title,
                                'row_number': row_idx
                            }
                        })

            self.logger.info(f"解析Excel文件完成: {file_path}, 提取 {len(qa_pairs)} 个问答对")
            return qa_pairs

        except Exception as e:
            self.logger.error(f"解析Excel文件失败: {file_path}, 错误: {e}")
            return []

    def parse_word(self, file_path: str) -> List[Dict[str, Any]]:
        """
        解析Word文档，提取问答对

        Args:
            file_path: Word文件路径

        Returns:
            包含问答对的字典列表
        """
        try:
            doc = Document(file_path)
            qa_pairs = []

            # 尝试不同的解析模式
            qa_pairs = self._extract_qa_from_tables(doc, file_path)
            if not qa_pairs:
                qa_pairs = self._extract_qa_from_paragraphs(doc, file_path)

            self.logger.info(f"解析Word文件完成: {file_path}, 提取 {len(qa_pairs)} 个问答对")
            return qa_pairs

        except Exception as e:
            self.logger.error(f"解析Word文件失败: {file_path}, 错误: {e}")
            return []

    def _extract_qa_from_tables(self, doc: Document, file_path: str) -> List[Dict[str, Any]]:
        """从表格中提取问答对"""
        qa_pairs = []

        for table_idx, table in enumerate(doc.tables):
            for row_idx, row in enumerate(table.rows):
                if len(row.cells) >= 2:
                    # 假设第一列是问题，第二列是答案
                    question = row.cells[0].text.strip()
                    answer = row.cells[1].text.strip()

                    # 检查是否是合理的问答
                    if (question and len(question) > 2 and
                        answer and len(answer) > 2 and
                        ('？' in question or '?' in question or '怎么' in question or '如何' in question)):
                        qa_pairs.append({
                            'id': len(qa_pairs) + 1,
                            'question': question,
                            'answer': answer,
                            'source': os.path.basename(file_path),
                            'metadata': {
                                'table_index': table_idx,
                                'row_number': row_idx + 1
                            }
                        })

        return qa_pairs

    def _extract_qa_from_paragraphs(self, doc: Document, file_path: str) -> List[Dict[str, Any]]:
        """从段落中提取问答对"""
        qa_pairs = []
        current_qa = None

        for para_idx, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            if not text:
                continue

            # 检查是否是问题（以问号结尾或包含问关键词）
            if ('？' in text or '?' in text) and len(text) > 5:
                # 保存上一个QA对
                if current_qa:
                    qa_pairs.append(current_qa)

                # 开始新的QA对
                current_qa = {
                    'id': len(qa_pairs) + 1,
                    'question': text,
                    'answer': '',
                    'source': os.path.basename(file_path),
                    'metadata': {
                        'paragraph_index': para_idx
                    }
                }
            # 如果当前有QA对且不是问题，可能是答案
            elif current_qa and not current_qa['answer']:
                current_qa['answer'] = text

        # 添加最后一个QA对
        if current_qa and current_qa['answer']:
            qa_pairs.append(current_qa)

        return qa_pairs

    def parse_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        解析目录中的所有Excel和Word文件

        Args:
            directory_path: 目录路径

        Returns:
            所有文件的问答对合并列表
        """
        all_qa_pairs = []

        if not os.path.exists(directory_path):
            self.logger.warning(f"目录不存在: {directory_path}")
            return all_qa_pairs

        # 查找所有支持的文件
        for file in os.listdir(directory_path):
            if file.endswith(('.xlsx', '.xls', '.docx')):
                file_path = os.path.join(directory_path, file)

                try:
                    if file.endswith(('.xlsx', '.xls')):
                        qa_pairs = self.parse_excel(file_path)
                    else:  # .docx
                        qa_pairs = self.parse_word(file_path)

                    all_qa_pairs.extend(qa_pairs)
                    self.logger.info(f"解析文件完成: {file}, 提取 {len(qa_pairs)} 个问答对")

                except Exception as e:
                    self.logger.error(f"解析文件失败: {file_path}, 错误: {e}")
                    continue

        self.logger.info(f"解析目录完成: {directory_path}, 共提取 {len(all_qa_pairs)} 个问答对")
        return all_qa_pairs

    def save_to_json(self, qa_pairs: List[Dict[str, Any]], output_path: str):
        """保存问答对到JSON文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
            self.logger.info(f"保存问答对到: {output_path}")
        except Exception as e:
            self.logger.error(f"保存JSON失败: {e}")
"""
测试Excel解析器
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.document_parser import ExcelParser

# 测试Excel文件路径
excel_path = r"C:\Users\jj\Desktop\RAG\报销.xlsx"

print("测试Excel解析器")
print("=" * 60)

if not os.path.exists(excel_path):
    print(f"❌ Excel文件不存在: {excel_path}")
    print("请先上传或创建Excel文件")
    sys.exit(1)

# 解析Excel文件
parser = ExcelParser(excel_path)

# 获取所有Sheet
print(f"\n📂 扫描Excel文件: {os.path.basename(excel_path)}")
print("-" * 60)

sheets = parser.get_all_sheets()
print(f"发现 {len(sheets)} 个Sheet:")
for sheet in sheets:
    print(f"  - {sheet}")

# 尝试解析每个Sheet
print("\n" + "=" * 60)
print("开始解析...")
print("=" * 60)

total_documents = 0

for sheet_name in sheets:
    print(f"\n📄 解析Sheet: {sheet_name}")
    print("-" * 60)

    documents = parser.parse_excel(sheet_name=sheet_name)

    if documents:
        print(f"✓ 成功解析 {len(documents)} 条问答对")

        # 显示前3条
        for i, doc in enumerate(documents[:3], 1):
            print(f"\n  {i}. 问题: {doc['question'][:50]}...")
            print(f"     来源: {doc['source']} (行: {doc['metadata']['row']})")
    else:
        print("  ❌ 未找到有效数据")

    total_documents += len(documents)

print("\n" + "=" * 60)
print(f"📊 总计: {total_documents} 条问答对")
print("=" * 60)

if total_documents > 0:
    print("\n✓ 解析测试成功!")
else:
    print("\n⚠️  未找到有效数据，请检查Excel格式")
    print("\n期望格式:")
    print("  - Sheet名称: 任意")
    print("  - 表头: 第2行（或其他行，需指定header_row参数）")
    print("  - 第A列: 问题")
    print("  - 第B列: 答案")

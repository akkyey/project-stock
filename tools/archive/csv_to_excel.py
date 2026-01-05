import argparse
import os
import sys

import pandas as pd

# srcモジュールを読み込めるようにパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
try:
    from src.excel_formatter import format_excel
except ImportError:
    # src/excel_formatter.py がない場合の簡易実装
    print("Warning: src.excel_formatter not found. Formatting will be skipped.")

    def format_excel(path):
        pass


def convert_csv_to_excel(csv_path, output_path=None):
    if not os.path.exists(csv_path):
        print(f"❌ Input file not found: {csv_path}")
        return

    if output_path is None:
        output_path = csv_path.replace(".csv", ".xlsx")

    print(f"🔄 Converting {os.path.basename(csv_path)} to Excel...")

    try:
        # CSV読み込み
        df = pd.read_csv(csv_path)

        # Excel保存
        df.to_excel(output_path, index=False, engine="openpyxl")

        # フォーマッター適用
        format_excel(output_path)

        print(f"✅ Created Formatted Excel: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Convert Analysis CSV to Formatted Excel"
    )
    parser.add_argument("input", nargs="?", help="Input CSV path")

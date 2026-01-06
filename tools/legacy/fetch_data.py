import argparse
import logging
import os

import pandas as pd
from src.database import StockDatabase
from src.logger import setup_logger
from src.utils import rotate_file_backup


def main():
    # 引数解析
    parser = argparse.ArgumentParser(
        description="Export DB to CSV (formerly fetch_data.py)"
    )
    parser.add_argument(
        "--use-backup",
        action="store_true",
        help="(Deprecated) Ignored in DB export mode",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="(Deprecated) Ignored in DB export mode"
    )
    parser.add_argument(
        "--save-db",
        action="store_true",
        default=True,
        help="(Deprecated) Always uses DB",
    )
    parser.parse_args()

    setup_logger()
    logging.getLogger(__name__)

    print("=== Stock Data Exporter (formerly Fetcher) ===")
    print("ℹ️  NOTE: Data fetching logic has been consolidated into 'collector.py'.")
    print(
        "ℹ️  This script now exports data from the Database to CSV files for backup/verification."
    )

    try:
        db = StockDatabase()
        conn = db._get_conn()

        print("🚀 Loading data from Database...")

        # Load latest market data joined with stock master
        # Using a similar query to analyzer.load_data_from_db but getting all columns needed for CSV
        query = """
        SELECT 
            m.*, s.name, s.sector, s.market
        FROM market_data m
        JOIN stocks s ON m.code = s.code
        WHERE m.entry_date = (
            SELECT MAX(entry_date) 
            FROM market_data m2 
            WHERE m2.code = m.code
        )
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            print("❌ No data found in Database. Please run 'collector.py' first.")
            return

        print(f"✅ Loaded {len(df)} records from DB.")

    except Exception as e:
        print(f"❌ Failed to load from DB: {e}")
        return

    # 3. 保存 (CSV Export)
    output_dir = "data/backup"
    os.makedirs(output_dir, exist_ok=True)

    # Clean up columns if needed (remove id, etc. if pure backup desire, but keeping all is safer)
    # Ensure column order or specific columns if necessary

    if "market" not in df.columns:
        save_path = os.path.join(output_dir, "stock_master.csv")
        rotate_file_backup(save_path)
        df.to_csv(save_path, index=False)
        print(f"✅ Saved all to {save_path} (Backup)")
        return

    def safe_filename(s):
        return "".join([c if c.isalnum() else "_" for c in str(s)])

    markets = df["market"].unique()
    print(f"\n💾 Saving split files to {output_dir} (Backup)...")

    total_saved = 0
    for market in markets:
        if not market:
            continue  # Skip empty market
        market_df = df[df["market"] == market]
        safe_market_name = safe_filename(market)
        filename = f"stock_master_{safe_market_name}.csv"
        save_path = os.path.join(output_dir, filename)

        try:
            rotate_file_backup(save_path)
            market_df.to_csv(save_path, index=False)
            print(f"   - {filename}: {len(market_df)} records")
            total_saved += len(market_df)
        except Exception as e:
            print(f"   ❌ Failed to save {filename}: {e}")

    print(f"✅ Total records exported: {total_saved}")


if __name__ == "__main__":
    main()

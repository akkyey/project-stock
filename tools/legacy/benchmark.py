import os
import time

import pandas as pd
from src.data_fetcher import DataFetcher
from src.excel_writer import ExcelWriter

from src.config_loader import ConfigLoader


def benchmark():
    print("=== ⏱️ Performance Benchmark Test ===")

    # Setup
    config_loader = ConfigLoader("config.yaml")
    config = config_loader.config
    fetcher = DataFetcher(config)
    writer = ExcelWriter(config)

    # Test Targets (有名な5銘柄)
    target_codes = ["7203", "9984", "6758", "8035", "6861"]
    print(f"Targets: {len(target_codes)} stocks")

    # --- 1. Network I/O (Fetching) ---
    print("\n1. Measuring Network I/O (Fetching data)...")
    start_time = time.time()

    fetched_data = []
    for code in target_codes:
        # fetch_single_stock は内部で yfinance (HTTP request) を呼ぶ
        data = fetcher._fetch_single_stock(code)
        if data:
            fetched_data.append(data)

    net_time = time.time() - start_time
    avg_net = net_time / len(target_codes)
    print(f"   Total Network Time: {net_time:.4f} sec")
    print(f"   Avg per Stock:      {avg_net:.4f} sec")

    if not fetched_data:
        print("❌ Network test failed. Aborting.")
        return

    df = pd.DataFrame(fetched_data)

    # --- 2. Disk I/O (CSV Save) ---
    print("\n2. Measuring Disk I/O (Saving CSV)...")
    csv_filename = "benchmark_test.csv"

    # 書き込み回数を増やして顕在化させる（100回書き込んで平均を取る）
    io_start_time = time.time()
    iterations = 100

    for _ in range(iterations):
        writer.save(df, csv_filename)

    io_time = (time.time() - io_start_time) / iterations
    print(f"   Avg Save Time (5 records): {io_time:.6f} sec")

    # --- 3. Disk I/O (DB Insert - Simulation) ---
    print("\n3. Measuring Disk I/O (SQLite Insert - Simulation)...")
    from src.database import StockDatabase

    db_path = "data/benchmark.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = StockDatabase(db_path=db_path)

    db_start_time = time.time()

    # Prepare data for DB
    # upsert_market_data expects list of dicts
    db.upsert_market_data(fetched_data)

    # Get IDs and save analysis results
    for row in fetched_data:
        # Get ID
        entry_date_str = str(row["entry_date"]).split(" ")[0]
        m_id = db.get_market_data_id(row["code"], entry_date_str)

        if m_id:
            record = {
                "market_data_id": m_id,
                "strategy_name": "bench_strategy",
                "quant_score": 50,
                "ai_sentiment": "Bench",
                "ai_reason": "Benchmark test",
                "ai_risk": "None",
                "score_long": 50,
                "score_short": 50,
                "score_gap": 0,
                "active_style": "benchmark",
                "row_hash": "hash_test_" + str(row["code"]),
            }
            db.save_analysis_result(record)

    db_time = time.time() - db_start_time
    avg_db = db_time / len(fetched_data)
    print(f"   Total DB Write Time: {db_time:.4f} sec")
    print(f"   Avg per Stock:       {avg_db:.6f} sec")

    # --- Conclusion ---
    print("\n=== 📊 Result Analysis ===")
    ratio = avg_net / (io_time if io_time > 0 else 0.0001)
    print(f"Network is {ratio:.1f}x slower than Disk Write.")

    if avg_net > 0.5:
        print("👉 Bottleneck is definitively NETWORK.")
        print("   Recommendation: Use 'fast_runner.py' (Parallelization).")
    elif io_time > 0.1:
        print("👉 Bottleneck might be DISK I/O.")
        print("   Recommendation: Use Pipeline/Stream processing.")
    else:
        print("👉 Both are fast enough. Python overhead might be the issue.")

    # Cleanup
    if os.path.exists(f"data/output/{csv_filename}"):
        os.remove(f"data/output/{csv_filename}")
    if os.path.exists(db_path):
        os.remove(db_path)


if __name__ == "__main__":
    benchmark()

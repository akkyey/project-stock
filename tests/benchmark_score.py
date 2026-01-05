import os
import sys
import time

import numpy as np
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.calc import Calculator


def run_benchmark():
    print("=== Starting Benchmark: Scalar vs Vectorized Score Calculation ===")

    # 1. Setup
    config = {
        "scoring_v2": {
            "styles": {"value_balanced": {"weight_fund": 0.7, "weight_tech": 0.3}},
            "tech_points": {
                "macd_bullish": 5,
                "rsi_oversold": 10,
                "rsi_overbought": -5,
                "trend_up": 5,
            },
            "macro": {"active_sector": "Technology"},
        },
        "scoring": {
            "base_score": 50,
            "thresholds": {"per": 15.0, "roe": 8.0},
            "points": {"per": 10, "roe": 10},
        },
    }
    calc = Calculator(config)

    # 2. Generate Dummy Data (N=30000)
    N = 30000
    print(f"Generating {N} records...")
    data = {
        "code": [f"{i}" for i in range(1000, 1000 + N)],
        "name": [f"Stock {i}" for i in range(N)],
        "per": np.random.uniform(5, 30, N),
        "pbr": np.random.uniform(0.5, 5, N),
        "roe": np.random.uniform(0, 20, N),
        "dividend_yield": np.random.uniform(0, 5, N),
        "operating_cf": np.random.uniform(-100, 1000, N),
        "macd_hist": np.random.uniform(-5, 5, N),
        "rsi_14": np.random.uniform(10, 90, N),
        "trend_up": np.random.choice([0, 1], N),
        "sector": np.random.choice(["Technology", "Finance", "Retail"], N),
    }
    df = pd.DataFrame(data)

    # 3. Vectorized Benchmark
    start_time = time.time()
    vec_result = calc.calc_v2_score(df, style="value_balanced")
    vec_time = time.time() - start_time
    print(f"Vectorized Time: {vec_time:.4f} sec")

    # 4. Scalar Benchmark (Loop)
    scalar_results = []
    start_time = time.time()
    for _, row in df.iterrows():
        # Convert row to dict as expected by scalar logic
        row_dict = row.to_dict()
        res = calc.calc_v2_score(row_dict, style="value_balanced")
        scalar_results.append(res)
    scalar_time = time.time() - start_time
    print(f"Scalar Loop Time: {scalar_time:.4f} sec")

    # 5. Speedup Factor
    if vec_time > 0:
        print(f"Speedup: {scalar_time / vec_time:.2f}x")

    # 6. Identity Verification
    print("\nVerifying Output Identity...")
    scalar_df = pd.DataFrame(scalar_results)

    # Compare key columns
    cols_to_check = ["quant_score", "score_long", "score_short", "score_gap"]

    mismatches = 0
    for col in cols_to_check:
        # Convert to numpy for comparison with tolerance
        v_vals = vec_result[col].values
        s_vals = scalar_df[col].values

        # Check for near equality (floating point tolerance)
        is_close = np.isclose(v_vals, s_vals, atol=1e-5)
        if not is_close.all():
            mismatch_idx = np.where(~is_close)[0]
            print(f"Mismatch in column '{col}': {len(mismatch_idx)} rows differ.")
            print(
                f"  Example: Idx {mismatch_idx[0]} -> Vec: {v_vals[mismatch_idx[0]]}, Scalar: {s_vals[mismatch_idx[0]]}"
            )
            mismatches += 1

    if mismatches == 0:
        print("✅ SUCCESS: Vectorized and Scalar outputs match perfectly.")
    else:
        print("❌ FAILURE: Outputs do not match.")
        exit(1)


if __name__ == "__main__":
    run_benchmark()

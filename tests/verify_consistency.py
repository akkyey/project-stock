import sys

import numpy as np
import pandas as pd


def verify_consistency(baseline_path, new_path):
    print(f"Comparing {baseline_path} vs {new_path}...")

    try:
        df_base = pd.read_csv(baseline_path, dtype={"code": str})
        df_new = pd.read_csv(new_path, dtype={"code": str})
    except Exception as e:
        print(f"Error loading CSVs: {e}")
        return False

    # Filter out columns that are expected to change or internal
    ignore_cols = [
        "analyzed_at",
        "updated_at",
        "row_hash",
        "_cache_label",
        "fetch_status",
        "ai_reason",
    ]
    # ai_reason might change if API call happens, but we used cache?
    # Ideally we compare scores.

    # Sort for alignment
    df_base = df_base.sort_values("code").reset_index(drop=True)
    df_new = df_new.sort_values("code").reset_index(drop=True)

    if len(df_base) != len(df_new):
        print(f"Row count mismatch: {len(df_base)} vs {len(df_new)}")
        return False

    mismatches = []

    # Common columns
    cols = [c for c in df_base.columns if c in df_new.columns and c not in ignore_cols]

    for col in cols:
        base_vals = df_base[col]
        new_vals = df_new[col]

        # Numeric check with tolerance
        if pd.api.types.is_numeric_dtype(base_vals) and pd.api.types.is_numeric_dtype(
            new_vals
        ):
            if not np.allclose(base_vals.fillna(0), new_vals.fillna(0), atol=1e-5):
                mismatches.append(col)
                print(f"Mismatch in numeric column: {col}")
                print(f"  Base: {base_vals.head().values}")
                print(f"  New : {new_vals.head().values}")
        else:
            # String check
            # For AI sentiment, allow match
            if not base_vals.fillna("").equals(new_vals.fillna("")):
                mismatches.append(col)
                print(f"Mismatch in string column: {col}")

    if mismatches:
        print(f"FAILED: Mismatches found in {len(mismatches)} columns: {mismatches}")
        return False

    print("SUCCESS: Results match perfectly (ignoring timestamps).")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python verify_consistency.py <baseline_csv> <new_csv>")
        sys.exit(1)

    success = verify_consistency(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)

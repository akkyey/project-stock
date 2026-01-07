import os
import sys

import pandas as pd
import yfinance as yf

# Submodule path
sys.path.append(os.path.join(os.getcwd(), "stock-analyzer4"))
from src.fetcher.technical import calc_technical_indicators

def simulate():
    # 銘柄を最小限に絞る
    codes = ["7203", "9984"] 
    data = []

    print("📊 Evaluating ranking impact...")
    for code in codes:
        try:
            print(f"  Fetching {code}...")
            ticker = yf.Ticker(f"{code}.T")
            hist = ticker.history(period="6mo")
            
            # Beta
            beta = ticker.info.get("beta")
            
            tech = calc_technical_indicators(hist)
            real_vol = tech.get("real_volatility")
            
            data.append({
                "Code": code,
                "Beta": beta,
                "RealVol": real_vol
            })
        except Exception as e:
            print(f"  Error for {code}: {e}")

    if not data:
        print("No data collected.")
        return

    df = pd.DataFrame(data)
    print("\n[Comparison Results]")
    print(df.to_string(index=False))

if __name__ == "__main__":
    simulate()

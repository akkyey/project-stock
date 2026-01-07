import pandas as pd
import yfinance as yf
import numpy as np
import os
import sys

# Submodule path
sys.path.append(os.path.join(os.getcwd(), "stock-analyzer4"))
from src.fetcher.technical import calc_technical_indicators

def simulate():
    # 銘柄特性の異なるものをピックアップ
    codes = {
        "7203": "Toyota (Stable/Large)",
        "8035": "Tokyo Electron (Growth/High-Tech)",
        "9101": "Nippon Yusen (Cyclical/High-Vol)",
        "4502": "Takeda (Defensive/Pharma)"
    }
    data = []

    print("📊 Evaluating multiple stocks...")
    for code, desc in codes.items():
        try:
            print(f"  Fetching {code} ({desc})...")
            ticker = yf.Ticker(f"{code}.T")
            hist = ticker.history(period="6mo")
            
            # Beta
            beta = ticker.info.get("beta")
            
            # Real Volatility
            tech = calc_technical_indicators(hist)
            real_vol = tech.get("real_volatility")
            
            data.append({
                "Code": code,
                "Type": desc,
                "Beta": beta,
                "RealVol (%)": f"{real_vol:.2f}" if real_vol else "N/A",
                "Penalty": "YES (-10)" if real_vol and real_vol > 50 else "no"
            })
        except Exception as e:
            print(f"  Error for {code}: {e}")

    df = pd.DataFrame(data)
    print("\n[Comparative Analysis Results]")
    print(df.to_string(index=False))

if __name__ == "__main__":
    simulate()

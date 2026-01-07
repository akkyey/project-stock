import os
import sys
import yaml
import pandas as pd
from dotenv import load_dotenv

# Submodule path
sys.path.append(os.path.join(os.getcwd(), "stock-analyzer4"))

from src.ai.agent import AIAgent
from src.fetcher.technical import calc_technical_indicators
import yfinance as yf

def get_sbg_data():
    code = "9984"
    ticker = yf.Ticker(f"{code}.T")
    hist = ticker.history(period="6mo")
    info = ticker.info
    
    tech = calc_technical_indicators(hist)
    
    # 手動でデータ辞書を作成
    data = {
        "code": code,
        "name": info.get("longName", "SoftBank Group Corp."),
        "sector": info.get("sector", "Communication Services"),
        "per": info.get("trailingPE"),
        "pbr": info.get("priceToBook"),
        "roe": info.get("returnOnEquity") * 100 if info.get("returnOnEquity") else None,
        "sales_growth": 5.0, # Dummy
        "operating_margin": 10.0, # Dummy
        "operating_cf": 1000000, # Dummy
        "sales": 5000000, # Dummy
        "volatility": info.get("beta"),
        "real_volatility": tech.get("real_volatility"),
        "macd_hist": tech.get("macd_hist"),
        "rsi_14": tech.get("rsi_14"),
        "trend_up": 1 if tech.get("trend_up") else 0,
        "score_value": 60,
        "score_growth": 70,
        "score_quality": 50,
        "score_trend": 80,
        "score_penalty": 0,
        "current_price": info.get("currentPrice")
    }
    return data

def run_test(label):
    print(f"\n--- Running AI Analysis: {label} ---")
    data = get_sbg_data()
    
    # .env から API キーを読み込む
    load_dotenv()
    
    agent = AIAgent(model_name="gemini-2.0-flash-exp")
    
    # config を手動設定
    with open("stock-analyzer4/config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    agent.set_config(config)
    
    prompt = agent._create_prompt(data, strategy_name="growth_quality")
    print(f"--- PROMPT START ---\n{prompt}\n--- PROMPT END ---")

    try:
        result = agent.analyze(data, strategy_name="growth_quality")
        print(f"Sentiment: {result.get('ai_sentiment')}")
        print(f"Summary: {result.get('ai_summary')}")
        print(f"Risk: {result.get('ai_risk')}")
        return result
    except Exception as e:
        print(f"AI Analysis failed: {e}")
        return None

if __name__ == "__main__":
    # 既存のプロンプトでの結果を保存
    # (まだコードを変更していないので Before として機能する)
    res_before = run_test("BEFORE (Standard Prompt)")
    with open("analysis_before.txt", "w") as f:
        f.write(str(res_before))

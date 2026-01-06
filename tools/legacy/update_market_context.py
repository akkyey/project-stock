import datetime
import os

import google.generativeai as genai
import yfinance as yf
from src.config_loader import load_config

# --- AI初期化 ---
config = load_config()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Warning: GEMINI_API_KEY not found. Mocking AI response.")
else:
    genai.configure(api_key=api_key)


def get_market_data():
    """主要指数のデータを取得してテキスト化する"""
    tickers = {
        "^N225": "Nikkei 225",
        "JPY=X": "USD/JPY",
        "^GSPC": "S&P 500",
        "^TNX": "US 10Y Yield",
        "^VIX": "VIX Index",
        "CL=F": "Crude Oil",
    }

    data_text = "=== Market Data ===\n"

    for symbol, name in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                current = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2]
                change = ((current - prev) / prev) * 100
                data_text += f"{name}: {current:.2f} (Change: {change:+.2f}%)\n"
            else:
                data_text += f"{name}: No Data\n"
        except Exception as e:
            data_text += f"{name}: Error ({e})\n"

    return data_text


def get_news_headlines():
    """ニュースヘッドラインを取得する"""
    news_text = "=== Related News ===\n"
    try:
        for symbol in ["^N225", "JPY=X"]:
            t = yf.Ticker(symbol)
            news_list = t.news
            if news_list:
                for item in news_list[:3]:
                    title = item.get("title", "No Title")
                    news_text += f"- {title}\n"
    except Exception:
        news_text += "No news fetched.\n"

    return news_text


import argparse  # noqa: E402

# ... (imports remain the same)


def generate_report(lang="ja"):
    print("🌍 Fetching Global Market Data (High-Res)...")
    market_data = get_market_data()

    print("📰 Fetching News Headlines...")
    news_data = get_news_headlines()

    full_input = f"{market_data}\n{news_data}"

    print(f"🧠 AI Analyst is thinking (Deep Analysis in {lang})...")

    if lang == "ja":
        prompt = f"""
        あなたは日本のヘッジファンドのチーフ・マーケット・ストラテジストです。
        提供された市場データとニュースに基づいて、株式スクリーニングのための**詳細な市況分析レポート**を作成してください。

        [入力データ]
        {full_input}

        [指示]
        1. **深く分析する**: 単なる要約ではなく、データの**含意 (Implications)** を説明してください（例：「金利上昇はハイテク株に打撃を与える」）。
        2. **構造**:
           - **市場センチメント**: 明確なステートメント（リスクオン / リスクオフ / 中立）。
           - **主要な要因**: なぜそうなっているかを説明する3つの箇条書き（例：米国のインフレ、日銀の政策）。
           - **セクターローテーション**: 今日、どの業種がアウトパフォームしそうか？
        3. **戦略シグナル**: 最後に一言で結論付けてください（BULLISH / BEARISH / NEUTRAL）。
        4. **言語**: **必ず日本語で出力してください。**

        [出力フォーマット]
        [Current Market Context ({datetime.date.today()})]
        1. 市場センチメント: [詳細な説明、約2-3文]
        2. 主要な要因:
           - [ポイント1: 深掘り]
           - [ポイント2: 深掘り]
           - [ポイント3: 深掘り]
        3. 注目セクター: [具体的なセクターをリストアップ、例：銀行、半導体]

        [STRATEGY_SIGNAL]: [BULLISH/BEARISH/NEUTRAL]
        """
        mock_report = f"[Current Market Context ({datetime.date.today()})]\nMock Report: 市場は安定しています。\n[STRATEGY_SIGNAL]: NEUTRAL"
    else:
        prompt = f"""
        You are a Chief Market Strategist for a Japanese hedge fund.
        Based on the provided market data and news, write a **detailed market context report** for stock screening.

        [Input Data]
        {full_input}

        [Instructions]
        1. **Analyze deeply**: Do not just summarize. Explain the *implications* of the data (e.g., "Yields are up, which hurts Tech stocks").
        2. **Structure**:
           - **Market Sentiment**: Clear statement (Risk-on / Risk-off / Neutral).
           - **Key Drivers**: 3 bullet points explaining WHY (e.g., US Inflation, BOJ Policy).
           - **Sector Rotation**: Which sectors are likely to outperform today?
        3. **Strategy Signal**: Conclude with a single word (BULLISH / BEARISH / NEUTRAL).

        [Output Format]
        [Current Market Context ({datetime.date.today()})]
        1. Sentiment: [Detailed explanation, approx 2-3 sentences]
        2. Key Drivers:
           - [Point 1: Deep dive]
           - [Point 2: Deep dive]
           - [Point 3: Deep dive]
        3. Focus Sectors: [List specific sectors, e.g., Banks, Semiconductors]

        [STRATEGY_SIGNAL]: [BULLISH/BEARISH/NEUTRAL]
        """
        mock_report = f"[Current Market Context ({datetime.date.today()})]\nMock Report: Market is stable.\n[STRATEGY_SIGNAL]: NEUTRAL"

    if not api_key:
        report = mock_report
    else:
        model = genai.GenerativeModel("gemini-2.0-flash-lite")
        response = model.generate_content(prompt)
        report = response.text

    with open("market_context.txt", "w", encoding="utf-8") as f:
        f.write(report)
        f.write("\n\n" + "-" * 20 + "\n[Raw Data Reference]\n" + full_input)

    print(f"\n✅ Market Context Updated (High Resolution - {lang})!")
    print(report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update market context.")
    parser.add_argument(
        "--lang",
        choices=["ja", "en"],
        default="ja",
        help="Output language (ja/en). Default is ja.",
    )
    args = parser.parse_args()

    generate_report(lang=args.lang)

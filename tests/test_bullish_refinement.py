import unittest

from src.reporter import StockReporter


class TestBullishRefinement(unittest.TestCase):
    def setUp(self):
        # 簡易的なReporterのモック（必要最小限）
        self.reporter = StockReporter()

    def test_bullish_refinement(self):
        # Data Structure Helper
        def make_info(sentiment, reason):
            return {
                "latest": {
                    "code": "9999",
                    "strategy_name": "TestStrat",
                    "ai_sentiment": sentiment,
                    "ai_reason": reason,
                    "ai_risk": "Low",
                    "quant_score": 80,
                    "ai_detail": "",
                },
                "data": {"code": "9999", "name": "TestCorp"},
                "strategies": ["TestStrat"],
            }

        # 1. Normal Aggressive (No specific keywords)
        info_agg = make_info("Bullish", "【結論】Bullish。EPS成長率が高く完璧。")
        res_agg, _ = self.reporter._format_single_item(info_agg, {})
        self.assertEqual(res_agg["AI_Rating"], "Bullish (Aggressive)")

        # 2. Defensive (Exception Keywords)
        info_def = make_info(
            "Bullish",
            "【結論】Bullish。極めて不本意ではあるが、PBR0.5倍の資産価値は無視できない。",
        )
        res_def, _ = self.reporter._format_single_item(info_def, {})
        self.assertEqual(res_def["AI_Rating"], "Bullish (Defensive)")

        # 3. Defensive (Already set by AI)
        info_exp = make_info("Bullish (Defensive)", "AIが最初からDefensiveと判定。")
        res_exp, _ = self.reporter._format_single_item(info_exp, {})
        self.assertEqual(res_exp["AI_Rating"], "Bullish (Defensive)")


if __name__ == "__main__":
    unittest.main()

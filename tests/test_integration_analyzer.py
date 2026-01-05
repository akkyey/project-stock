import unittest
from unittest.mock import patch

import pandas as pd
import pytest

from src.analyzer import StockAnalyzer


@pytest.mark.integration
class TestStockAnalyzerIntegration(unittest.TestCase):
    def setUp(self):
        # Config valid for initialization
        self.config = {
            "data": {
                "jp_stock_list": "dummy_list.csv",
                "output_path": "dummy_output.csv",
            },
            "ai": {"interval_sec": 0},
            "strategies": {"value_strict": {}},
            "scoring_v2": {},
        }

    @patch("src.analyzer.AnalysisEngine")
    @patch("src.analyzer.DataProvider")
    @patch("src.analyzer.AIAgent")
    @patch("src.analyzer.ResultWriter")
    def test_run_analysis_flow(self, MockWriter, MockAI, MockProvider, MockEngine):
        """Analyze.run_analysis の主要フローを通す統合テスト"""
        # --- 1. Mock Setup ---

        # Provider
        provider_instance = MockProvider.return_value
        # load_latest_market_data returns DF to analyze
        provider_instance.load_latest_market_data.return_value = pd.DataFrame(
            [
                {
                    "code": "1001",
                    "name": "Stock A",
                    "sector": "Tech",
                    "current_price": 1000,
                },
                {
                    "code": "1002",
                    "name": "Stock B",
                    "sector": "Food",
                    "current_price": 500,
                },
            ]
        )
        # get_ai_cache returns nothing (needs analysis)
        provider_instance.get_ai_cache.return_value = (None, "hash")

        # Engine
        engine_instance = MockEngine.return_value
        # calculate_scores returns DF (pass through)
        engine_instance.calculate_scores.return_value = (
            provider_instance.load_latest_market_data.return_value
        )
        # filter_and_rank returns list of candidates
        engine_instance.filter_and_rank.return_value = pd.DataFrame(
            [
                {"code": "1001", "name": "Stock A", "quant_score": 80},
                {"code": "1002", "name": "Stock B", "quant_score": 40},
            ]
        )

        # AI Agent
        ai_instance = MockAI.return_value
        ai_instance.analyze.return_value = {
            "ai_sentiment": "Bullish",
            "ai_reason": "Good",
            "ai_risk": "Low",
            "ai_horizon": "Long",
        }

        # Writer
        writer_instance = MockWriter.return_value

        # --- 2. Execution ---
        analyzer = StockAnalyzer(self.config)

        # Mode: normal
        analyzer.run_analysis(limit=2)

        # --- 3. Assertions ---
        # Provider: Load Data
        provider_instance.load_latest_market_data.assert_called()

        # Engine: Calculate & Filter
        engine_instance.calculate_scores.assert_called()
        engine_instance.filter_and_rank.assert_called()

        # AI: Analyze called
        # We loop through candidates. 2 items.
        self.assertEqual(ai_instance.analyze.call_count, 2)

        # Provider: Save Result
        provider_instance.save_analysis_result.assert_called()

        # Writer: Save
        writer_instance.save.assert_called()

        # Provider: Cleanup
        provider_instance.stock_db.cleanup_and_optimize.assert_called()

    @patch("src.analyzer.AnalysisEngine")
    @patch("src.analyzer.DataProvider")
    @patch("src.analyzer.AIAgent")
    @patch("src.analyzer.ResultWriter")
    def test_run_analysis_screening_stage(
        self, MockWriter, MockAI, MockProvider, MockEngine
    ):
        """Stage: screening の動作確認"""

        # Setup mocks
        provider_instance = MockProvider.return_value
        provider_instance.load_latest_market_data.return_value = pd.DataFrame(
            [{"code": "2001"}]
        )

        engine_instance = MockEngine.return_value
        engine_instance.calculate_scores.return_value = pd.DataFrame([{"code": "2001"}])
        engine_instance.filter_and_rank.return_value = pd.DataFrame(
            [{"code": "2001", "name": "S", "quant_score": 90}]
        )

        analyzer = StockAnalyzer(self.config)
        analyzer.run_analysis(stage="screening")

        # AI Agent should NOT be called
        MockAI.return_value.analyze.assert_not_called()

        # Writer should be called to save screening results
        MockWriter.return_value.save.assert_called()


if __name__ == "__main__":
    unittest.main()

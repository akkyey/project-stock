import unittest
from datetime import datetime
from unittest.mock import patch

from src.provider import DataProvider

# AnalysisStatus import removed


class TestProviderCoverage(unittest.TestCase):
    def setUp(self):
        self.config = {
            "ai": {"model_name": "test-model", "cache_days": 7},
            "strategies": {"test_strat": {}},
        }
        with patch("src.provider.StockDatabase"):
            self.provider = DataProvider(self.config)

    @patch("src.provider.generate_row_hash")
    def test_get_ai_cache_logic(self, mock_hash):
        """Test AI Cache validation logic branches"""
        mock_hash.return_value = "new_hash"
        mock_db = self.provider.stock_db

        # Define mock behavior for get_ai_cache (Strict Match)
        # Case 1: Strict Match Found
        mock_db.get_ai_cache.return_value = {
            "result": "strict_hit",
            "row_hash": "new_hash",
        }
        res, reason = self.provider.get_ai_cache(
            {"code": "1001"}, "test_strat", validity_days=0
        )
        self.assertEqual(res["result"], "strict_hit")
        self.assertEqual(reason, "new_hash")  # Returned tuple is (cached, row_hash)

        # Case 2: Strict Miss, Smart Cache Disable (validity=0)
        mock_db.get_ai_cache.return_value = None
        res, reason = self.provider.get_ai_cache(
            {"code": "1001"}, "test_strat", validity_days=0
        )
        self.assertIsNone(res)

        # Case 3: Strict Miss, Smart Cache Hit (Valid triggers)
        mock_db.get_ai_cache.return_value = None
        mock_db.get_ai_smart_cache.return_value = {
            "result": "smart_hit",
            "cached_price": 100,
            "quant_score": 80,
        }

        # 3a. No triggers
        res, reason = self.provider.get_ai_cache(
            {"code": "1001", "current_price": 105}, "test_strat", validity_days=7
        )
        self.assertIsNotNone(res)
        self.assertTrue(res.get("_is_smart_cache"))

        # 3b. Price Trigger (Within Limit)
        # Limit 10%, Diff 5/100 = 5% -> OK
        triggers = {"price_change_pct": 10}
        res, _ = self.provider.get_ai_cache(
            {"code": "1001", "current_price": 105},
            "test_strat",
            validity_days=7,
            refresh_triggers=triggers,
        )
        self.assertIsNotNone(res)

        # 3c. Price Trigger (Exceeded)
        # Limit 1%, Diff 5% -> None
        triggers = {"price_change_pct": 1}
        res, _ = self.provider.get_ai_cache(
            {"code": "1001", "current_price": 105},
            "test_strat",
            validity_days=7,
            refresh_triggers=triggers,
        )
        self.assertIsNone(res)

        # 3d. Score Trigger (Within Limit)
        # Limit 5pts, Diff 0 -> OK
        triggers = {"score_change_point": 5}
        # mock_db.get_ai_smart_cache returns score 80
        res, _ = self.provider.get_ai_cache(
            {"code": "1001", "quant_score": 82},
            "test_strat",
            validity_days=7,
            refresh_triggers=triggers,
        )
        self.assertIsNotNone(res)

        # 3e. Score Trigger (Exceeded)
        # Limit 1pt, Diff 2 -> None
        triggers = {"score_change_point": 1}
        res, _ = self.provider.get_ai_cache(
            {"code": "1001", "quant_score": 82},
            "test_strat",
            validity_days=7,
            refresh_triggers=triggers,
        )
        self.assertIsNone(res)

    def test_save_analysis_result(self):
        """Test save logic"""
        mock_db = self.provider.stock_db

        # Success Case
        result_data = {
            "market_data_id": 123,
            "quant_score": 90.0,
            "ai_sentiment": "Bullish",
            "analyzed_at": datetime(2025, 1, 1),
        }
        self.provider.save_analysis_result(result_data, "test_strat")
        mock_db.save_analysis_result.assert_called_once()
        call_args = mock_db.save_analysis_result.call_args[0][0]
        self.assertEqual(call_args["market_data"], 123)
        self.assertEqual(call_args["strategy_name"], "test_strat")

        # Missing ID Case
        mock_db.save_analysis_result.reset_mock()
        self.provider.save_analysis_result({}, "test_strat")
        mock_db.save_analysis_result.assert_not_called()

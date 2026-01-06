import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

# Path resolution to include stock-analyzer4/src in sys.path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, "stock-analyzer4"))

from src.analyzer import StockAnalyzer  # noqa: E402
from src.calc import Calculator  # noqa: E402
from src.calc.strategies.turnaround import TurnaroundStrategy  # noqa: E402
from src.database_factory import DatabaseFactory  # noqa: E402
from src.validation_engine import ValidationEngine  # noqa: E402


class TestAnalyzerEngine(unittest.TestCase):
    def setUp(self):
        """Test setup"""
        DatabaseFactory.reset()
        # Dummy Config v8.0 style
        self.dummy_config = {
            "api": {"key": "test_key"},
            "system": {"concurrency": 1},
            "strategies": {
                "test_strat": {
                    "base_score": 50,
                    "min_requirements": {"roe": 5.0},
                    "thresholds": {"per": 15.0, "roe": 8.0, "debt_equity_ratio": 1.0},
                    "points": {"per": 10, "roe": 10, "debt_equity_ratio": 10},
                    "default_style": "value_balanced",
                }
            },
            "scoring_v2": {
                "styles": {"value_balanced": {"weight_fund": 0.7, "weight_tech": 0.3}},
                "tech_points": {"macd_bullish": 10, "rsi_oversold": 10},
                "macro": {},
            },
            "sector_policies": {
                "銀行業": {
                    "na_allowed": [
                        "debt_equity_ratio",
                        "free_cf",
                        "operating_cf",
                        "payout_ratio",
                    ],
                    "score_exemptions": ["debt_equity_ratio"],
                    "ai_prompt_excludes": [],
                },
                "default": {
                    "na_allowed": [],
                    "score_exemptions": [],
                    "ai_prompt_excludes": [],
                },
            },
            "metadata_mapping": {
                "metrics": {
                    "Op CF Margin": "operating_cf",
                    "Debt/Equity Ratio": "debt_equity_ratio",
                    "Free CF": "free_cf",
                    "Operating Margin": "operating_margin",
                    "ROE": "roe",
                    "PER": "per",
                    "PBR": "pbr",
                    "Dividend Yield": "dividend_yield",
                }
            },
            "current_strategy": "test_strat",
            "ai": {"model_name": "gemini-pro", "interval_sec": 0.1},
        }

    def tearDown(self):
        DatabaseFactory.reset()

    # --- Calculator Logic ---

    def test_calculator_logic(self):
        print("Testing Calculator (via ScoringEngine)...")
        calc = Calculator(self.dummy_config)

        # 1. Normal
        row = {"per": 10.0, "roe": 10.0}
        score = calc.calc_quant_score(row, strategy_name="test_strat")
        self.assertEqual(score, 64.0)
        print("  - Normal calculation -> OK")

        # 2. None
        row_none = {"per": None, "roe": 10.0}
        score_none = calc.calc_quant_score(row_none, strategy_name="test_strat")
        self.assertEqual(score_none, 57.0)
        print("  - None handling -> OK")

        # 3. Dividend Logic (Needs explicit config update in test or rely on setUp defaults if sufficient)
        # Re-applying specific config for this test locally to be safe
        self.dummy_config["strategies"]["test_strat"]["points"]["dividend_yield"] = 10
        self.dummy_config["strategies"]["test_strat"]["thresholds"][
            "dividend_yield"
        ] = 3.0
        calc = Calculator(self.dummy_config)  # refresh

        row_div = {"dividend_yield": 4.0, "operating_cf": -100}  # Risk
        score_div = calc.calc_quant_score(row_div, strategy_name="test_strat")
        self.assertEqual(score_div, 50.0)
        print("  - Dividend Logic Safe Check -> OK")

    def test_score_normalization(self):
        """[v8.0] Sector Normalization"""
        print("Testing Score Normalization (Sector Exemptions)...")
        # Reuse dummy config but ensure thresholds are set for Debt/Equity
        # (Setup already has them now)
        calc = Calculator(self.dummy_config)

        # 1. Bank (Exempt)
        bank_row = {"per": 10.0, "roe": 10.0, "sector": "銀行業"}
        result = calc.calc_v2_score(bank_row, strategy_name="test_strat")

        # Debug info if fail
        if result["quant_score"] != 71.0:
            print(f"DEBUG: Score={result['quant_score']}, Details={result}")

        self.assertEqual(result["quant_score"], 71.0)
        print(f"  - Bank sector normalization: {result['quant_score']} -> OK")

        # 2. Normal (No Exempt)
        normal_row = {
            "per": 10.0,
            "roe": 10.0,
            "debt_equity_ratio": 0.5,
            "sector": "小売業",
        }
        result_normal = calc.calc_v2_score(normal_row, strategy_name="test_strat")
        self.assertEqual(result_normal["quant_score"], 71.0)
        print(f"  - Normal sector: {result_normal['quant_score']} -> OK")

    # --- Analyzer / AI Agent Integration ---

    def test_process_single_stock(self):
        """Testing StockAnalyzer.process_single_stock"""
        print("Testing StockAnalyzer.process_single_stock...")

        with (
            patch("src.ai.agent.AIAgent._generate_content_with_retry") as mock_api,
            patch("src.provider.DataProvider.get_ai_cache") as mock_get_cache,
            patch("src.provider.DataProvider.save_analysis_result") as mock_save,
        ):
            analyzer = StockAnalyzer(self.dummy_config)
            analyzer.ai_agent.validator = ValidationEngine(self.dummy_config)

            row_data = {
                "code": "1001",
                "name": "Test",
                "current_price": 1000.0,
                "operating_margin": 10.0,
                "operating_cf": 100.0,
                "per": 10.0,
                "pbr": 1.0,
                "roe": 10.0,
                "quant_score": 80,
                "entry_date": "2025-01-01",
                "market_data_id": 1,
            }

            mock_get_cache.return_value = (None, "cachedhash")
            # Update to match required format:
            # 1. Summary: 【結論】...｜【強み】...｜【懸念】...
            # 2. Detail: Must contain ① and ⑦ (sections)
            mock_api.return_value = MagicMock(
                text='{"ai_sentiment": "Bullish", "ai_reason": "【結論】Bullish｜【強み】財務盤石｜【懸念】特になし", "ai_detail": "詳細分析:\\n① 業績動向: 良好\\n...\\n⑦ 総合評価: A"}'
            )

            result = analyzer.process_single_stock(row_data, "test_strat")

            self.assertEqual(result["ai_sentiment"], "Bullish")
            self.assertEqual(result["row_hash"], "cachedhash")
            mock_save.assert_called_once()

        print("Process Single Stock Flow -> OK")

    @patch("src.provider.DataProvider.load_latest_market_data")
    @patch("src.analyzer.StockAnalyzer.process_single_stock")
    def test_analyzer_limit_loop(self, mock_process, mock_load):
        print("Testing Analyzer Limit Logic...")
        # 5 items
        data = [{"code": str(i), "name": f"Stock {i}"} for i in range(5)]
        mock_load.return_value = pd.DataFrame(data)

        analyzer = StockAnalyzer(self.dummy_config)
        analyzer.writer.save = MagicMock()
        mock_process.return_value = {"ai_sentiment": "Neutral", "_is_cached": False}

        analyzer.run_analysis(limit=3)
        self.assertEqual(mock_process.call_count, 3)
        print(f"Analyzer limit processed {mock_process.call_count}/5 -> OK")

    @patch("src.provider.DataProvider.load_latest_market_data")
    @patch("src.analyzer.StockAnalyzer.process_single_stock")
    def test_analyzer_circuit_breaker(self, mock_process, mock_load):
        print("Testing Analyzer Circuit Breaker logic...")
        data = [{"code": "1", "name": "S1"}]
        mock_load.return_value = pd.DataFrame(data)

        mock_process.return_value = {
            "ai_sentiment": "Error",
            "ai_reason": "API Error: 429 Quota Exceeded",
        }

        analyzer = StockAnalyzer(self.dummy_config)
        analyzer.writer.save = MagicMock()

        analyzer.run_analysis()
        self.assertEqual(mock_process.call_count, 1)
        print("Circuit Breaker aborted -> OK")

    def test_analyzer_smart_cache(self):
        print("Testing Analyzer Smart Cache logic...")
        from datetime import datetime

        with (
            patch("src.ai.agent.AIAgent._generate_content_with_retry") as mock_api,
            patch("src.provider.DataProvider.get_ai_cache") as mock_get_cache,
            patch("src.provider.DataProvider.save_analysis_result"),
        ):
            # 1. Full Match
            mock_get_cache.return_value = (
                {"ai_sentiment": "Bullish", "_is_cached": True},
                "hash_match",
            )
            analyzer = StockAnalyzer(self.dummy_config)
            row_data = {"code": "1001", "name": "Test"}
            res = analyzer.process_single_stock(row_data, "strat")
            self.assertEqual(res["_cache_label"], "[Cached]")
            self.assertFalse(mock_api.called)

            # 2. Smart Match
            mock_get_cache.reset_mock()
            mock_get_cache.return_value = (
                {
                    "ai_sentiment": "Neutral",
                    "analyzed_at": datetime.now(),
                    "_is_smart_cache": True,
                },
                "new_hash",
            )
            res = analyzer.process_single_stock(row_data, "strat")
            self.assertIn("Smart Cache", res["_cache_label"])
            self.assertFalse(mock_api.called)

        print("Smart Cache Logic -> OK")

    def test_analyzer_smart_refresh(self):
        print("Testing Analyzer Smart Refresh...")
        from datetime import datetime

        with (
            patch("src.ai.agent.AIAgent._generate_content_with_retry") as mock_api,
            patch("src.provider.DataProvider.get_ai_cache") as mock_get_cache,
        ):
            analyzer = StockAnalyzer(self.dummy_config)
            analyzer.ai_agent.validator = ValidationEngine(self.dummy_config)
            row_data = {
                "code": "1001",
                "name": "Test",
                "current_price": 1000,
                "quant_score": 80,
            }

            triggers = {"price_change_pct": 5.0, "score_change_point": 10.0}
            analyzer.config["ai"] = {
                "refresh_triggers": triggers,
                "model_name": "gemini-pro",
            }

            # 1. Within range (Use Cache)
            mock_get_cache.return_value = (
                {
                    "ai_sentiment": "Bullish",
                    "analyzed_at": datetime.now(),
                    "_is_smart_cache": True,
                    "cached_price": 1010,
                    "quant_score": 82,
                },
                "hash_mismatch",
            )
            res = analyzer.process_single_stock(row_data, "strat")
            self.assertTrue(res.get("_is_cached"))
            self.assertIn("Smart Cache", res.get("_cache_label"))

            # 2. Out of range (Re-analyze)
            mock_get_cache.reset_mock()
            mock_get_cache.return_value = (None, "hash_mismatch")
            mock_api.return_value = MagicMock(text='{"ai_sentiment": "Neutral"}')

            res = analyzer.process_single_stock(row_data, "strat")
            self.assertFalse(res.get("_is_cached"))
            self.assertEqual(res.get("_cache_label"), "🚀 Analyzing...")
        print("Smart Refresh Logic -> OK")

    # --- Validation ---

    def test_validate_task_data(self):
        print("\nTesting ValidationEngine Logic (validate_stock_data)...")
        config = self.dummy_config
        engine = ValidationEngine(config)

        # 1. Valid Data
        valid_data = {
            "code": "1001",
            "current_price": 1000,
            "operating_cf": 100,
            "operating_margin": 10.0,
            "per": 15.0,
            "pbr": 1.0,
            "roe": 10.0,
            "sector": "Unknown",
        }
        is_val, issues = engine.validate_stock_data(valid_data, strategy="normal")
        self.assertTrue(is_val, msg=f"Should be valid: {issues}")

        # 2. Missing Critical (Tier 1) - operating_cf
        missing_data = valid_data.copy()
        missing_data["operating_cf"] = None
        missing_data["sector"] = "小売業"  # Ensure not bank
        is_val, issues = engine.validate_stock_data(missing_data, strategy="normal")
        self.assertFalse(is_val)
        self.assertTrue(
            any("Missing Critical" in i for i in issues), f"Issues: {issues}"
        )

        # 3. Bank Exempt (operating_cf missing but allowed for Bank)
        bank_data = missing_data.copy()
        bank_data["sector"] = "銀行業"
        is_val, issues = engine.validate_stock_data(bank_data, strategy="normal")
        self.assertTrue(is_val, msg=f"Bank should be exempt: {issues}")

        # 4. Score Mismatch (Value Strict with low score)
        low_score_data = valid_data.copy()
        low_score_data["score_value"] = 5.0  # Threshold is 15
        is_val, issues = engine.validate_stock_data(
            low_score_data, strategy="value_strict"
        )
        self.assertFalse(is_val)
        self.assertTrue(any("Score Mismatch" in i for i in issues), f"Issues: {issues}")

        # 5. Abnormal Value (PER > 500)
        abnormal_data = valid_data.copy()
        abnormal_data["per"] = 600.0
        is_val, issues = engine.validate_stock_data(abnormal_data, strategy="normal")
        self.assertFalse(is_val)
        self.assertTrue(
            any("valuation_bubble" in i for i in issues), f"Issues: {issues}"
        )

        print("ValidationEngine Tests -> OK")

    def test_turnaround_penalty(self):
        print("\nTesting Turnaround Spec ROE Penalty...")

        data = pd.DataFrame(
            [
                {
                    "code": "T001",
                    "pbr": 0.5,
                    "sales_growth": 50.0,
                    "roe": np.nan,
                    "profit_status": "turnaround",
                    "sector": "Unknown",
                }
            ]
        )

        strat = TurnaroundStrategy({})
        result = strat.calculate_score(data)
        final_score = result.iloc[0]["quant_score"]
        self.assertLess(final_score, 100.0)

        data_ok = data.copy()
        data_ok["roe"] = 15.0
        result_ok = strat.calculate_score(data_ok)
        final_score_ok = result_ok.iloc[0]["quant_score"]

        self.assertGreater(final_score_ok, final_score)
        print("  Penalty Check: Missing ROE < Normal ROE -> OK")


if __name__ == "__main__":
    unittest.main()

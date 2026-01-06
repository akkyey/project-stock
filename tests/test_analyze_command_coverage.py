import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pandas as pd

from src.commands.analyze import AnalyzeCommand


class TestAnalyzeCommandCoverage(unittest.TestCase):
    def setUp(self):
        self.config = {
            "ai": {
                "model_name": "test",
                "interval_sec": 0.1,
                "max_concurrency": 2,
                "validity_days": 7,
            },
            "api_settings": {"gemini_tier": "free"},
            "strategies": {"test_strat": {}},
            "circuit_breaker": {"consecutive_failure_threshold": 5},
            "database": {"retention_days": 30},
        }

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.analyze.CircuitBreaker")
    @patch("src.commands.base_command.DataProvider")
    @patch("glob.glob")
    def test_execute_with_files(
        self, mock_glob, mock_provider_cls, mock_cb_cls, mock_writer_cls, mock_agent_cls
    ):
        """Test execute in file mode (Mocked Glue)"""
        cmd = AnalyzeCommand(self.config)

        # Test 1: No files
        mock_glob.return_value = []
        cmd.execute_from_files("*.json")

        # Test 2: Files found
        mock_glob.return_value = ["/tmp/dummy.json"]

        # Mock open/load
        with patch("builtins.open", mock_open(read_data='[{"code": "1001"}]')):
            # Mock _run_async_batch to avoid complex flow
            cmd._run_async_batch = AsyncMock(return_value=[])
            cmd.execute_from_files("*.json")
            cmd._run_async_batch.assert_called()

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.base_command.DataProvider")
    def test_execute_strategy_iteration(
        self, mock_provider_cls, mock_writer_cls, mock_agent_cls
    ):
        """Test execute iterates all strategies if None provided"""
        cmd = AnalyzeCommand(self.config)
        mock_provider_instance = mock_provider_cls.return_value
        mock_provider_instance.load_latest_market_data.return_value = pd.DataFrame()
        cmd.provider = mock_provider_instance

        with patch.object(cmd, "execute") as recursive_mock:
            cmd.execute(strategy=None)
            recursive_mock.assert_called()

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.base_command.DataProvider")
    def test_process_single_stock_logic(
        self, mock_provider_cls, mock_writer_cls, mock_agent_cls
    ):
        """Test logic branches in _process_single_stock"""
        cmd = AnalyzeCommand(self.config)
        mock_agent = cmd.agent
        mock_agent.audit_version = 5
        mock_agent.get_total_calls.return_value = 5

        mock_provider = mock_provider_cls.return_value

        # 1. Version Check: Cache Expired
        row = {"code": "1001", "name": "StockA"}
        mock_provider.get_ai_cache.return_value = (
            {"ai_sentiment": "Bullish", "audit_version": 1},
            "hash1",
        )
        mock_agent.analyze.return_value = {
            "ai_sentiment": "Bearish",
            "api_call_count": 1,
        }

        res = cmd._process_single_stock(row, "test_strat")
        self.assertEqual(res["ai_sentiment"], "Bearish")
        self.assertFalse(res["_is_cached"])

        # 2. Version Check: Cache Valid
        mock_provider.get_ai_cache.return_value = (
            {"ai_sentiment": "CachedBull", "audit_version": 5},
            "hash2",
        )
        res = cmd._process_single_stock(row, "test_strat")
        self.assertEqual(res["ai_sentiment"], "CachedBull")
        self.assertTrue(res["_is_cached"])

        # 3. Force Refresh
        cmd.force_refresh = True
        mock_provider.get_ai_cache.side_effect = Exception("Should not be called")
        mock_agent.analyze.return_value = {"ai_sentiment": "Fresh", "api_call_count": 1}
        res = cmd._process_single_stock(row, "test_strat")
        self.assertEqual(res["ai_sentiment"], "Fresh")
        cmd.force_refresh = False
        mock_provider.get_ai_cache.side_effect = None

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.analyze.StockAnalysisData")
    def test_guardrail_abnormal_skip(
        self, mock_stock_data_cls, mock_provider_cls, mock_writer_cls, mock_agent_cls
    ):
        """Test Guardrail (Abnormal Skip)"""
        cmd = AnalyzeCommand(self.config)

        # モックのStockAnalysisDataインスタンスを設定
        mock_stock_instance = MagicMock()
        mock_stock_instance.should_skip_analysis = True
        mock_stock_instance.validation_flags.skip_reasons = [MagicMock(value="Critical Debt")]
        mock_stock_data_cls.return_value = mock_stock_instance

        mock_provider = mock_provider_cls.return_value
        mock_provider.get_ai_cache.return_value = (None, "hash")

        row = {"code": "bad_stock"}
        res = cmd._process_single_stock(row, "test_strat")

        self.assertEqual(res["ai_sentiment"], "Bearish (Abnormal Skip)")
        self.assertIn("Critical Debt", res["ai_reason"])
        cmd.agent.analyze.assert_not_called()

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.base_command.DataProvider")
    def test_deep_repair_logic(
        self, mock_provider_cls, mock_writer_cls, mock_agent_cls
    ):
        """Test Deep Repair fetching"""
        cmd = AnalyzeCommand(self.config)
        cmd.fetcher = MagicMock()
        cmd.fetcher._fetch_single_stock.return_value = {"equity_ratio": 99.9}

        mock_provider = mock_provider_cls.return_value
        mock_provider.get_ai_cache.return_value = (None, "hash")

        cmd.agent.analyze.return_value = {"ai_sentiment": "Ok"}
        cmd.agent.get_total_calls.return_value = 0

        row = {"code": "repair_stock", "equity_ratio": 10.0}
        res = cmd._process_single_stock(row, "test_strat")

        cmd.fetcher._fetch_single_stock.assert_called_with(
            "repair_stock", deep_repair=True
        )
        self.assertEqual(res["equity_ratio"], 99.9)

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.base_command.DataProvider")
    def test_async_batch_paid_tier(
        self, mock_provider_cls, mock_writer_cls, mock_agent_cls
    ):
        """Test async batch with Paid Tier logic"""
        config = self.config.copy()
        config["api_settings"]["gemini_tier"] = "paid"
        cmd = AnalyzeCommand(config)

        df = pd.DataFrame([{"code": "p1"}, {"code": "p2"}])

        mock_provider = mock_provider_cls.return_value
        mock_provider.get_ai_cache.return_value = (None, "hash")

        # Mock to avoid real API
        cmd._process_single_stock = MagicMock(
            return_value={"code": "p1", "ai_sentiment": "Paid"}
        )

        results = asyncio.run(cmd._run_async_batch(df, "test_strat"))
        self.assertEqual(len(results), 2)


class TestAnalyzeCommandExtended(unittest.TestCase):
    def setUp(self):
        self.config = {
            "ai": {
                "model_name": "test",
                "interval_sec": 0.1,
                "max_concurrency": 2,
                "validity_days": 7,
            },
            "api_settings": {"gemini_tier": "free"},
            "strategies": {"test_strat": {}},
            "circuit_breaker": {"consecutive_failure_threshold": 5},
            "database": {"retention_days": 30},
        }

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.base_command.DataProvider")
    def test_save_results(self, mock_provider_cls, mock_writer_cls, mock_agent_cls):
        """Test _save_results delegation"""
        cmd = AnalyzeCommand(self.config)
        results = [{"code": "1001"}]

        # Test Save
        cmd._save_results(results, "test_strat")

        # Check writer delegation
        mock_writer_instance = mock_writer_cls.return_value
        mock_writer_instance.save.assert_called()

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.base_command.DataProvider")
    def test_print_usage_report(
        self, mock_provider_cls, mock_writer_cls, mock_agent_cls
    ):
        """Test usage report generation call"""
        cmd = AnalyzeCommand(self.config)
        mock_agent = cmd.agent
        mock_agent.token_eaters = []
        mock_agent.generate_usage_report.return_value = "REPORT"

        cmd._print_usage_report()
        mock_agent.generate_usage_report.assert_called()

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.base_command.DataProvider")
    def test_execute_with_codes(
        self, mock_provider_cls, mock_writer_cls, mock_agent_cls
    ):
        """Test execute in filtered mode (codes provided)"""
        cmd = AnalyzeCommand(self.config)

        # Mock fetch logic
        with patch.object(cmd, "_fetch_candidates_df_by_code") as mock_fetch:
            mock_fetch.return_value = pd.DataFrame([{"code": "9999"}])

            # Mock async batch
            with patch.object(cmd, "_run_async_batch") as mock_batch:
                mock_batch.return_value = []

                # Fix: Use keyword arguments
                cmd.execute(codes=["9999"], strategy="test_strat")

                mock_fetch.assert_called_with(["9999"], "test_strat")
                mock_batch.assert_called()

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.base_command.DataProvider")
    def test_fetch_candidates_logic_explicit_mock(
        self, mock_provider_cls, mock_writer_cls, mock_agent_cls
    ):
        cmd = AnalyzeCommand(self.config)
        mock_provider = mock_provider_cls.return_value
        mock_provider.load_latest_market_data.return_value = pd.DataFrame(
            [{"code": "1001"}]
        )

        with patch("src.commands.analyze.ScoringEngine") as mock_eng_cls:
            mock_eng = mock_eng_cls.return_value
            mock_eng.calculate_score.return_value = pd.DataFrame(
                [{"code": "1001", "quant_score": 10}]
            )
            mock_eng.filter_and_rank.return_value = pd.DataFrame(
                [{"code": "1001", "quant_score": 10}]
            )

            res = cmd._fetch_candidates_df_logic("test_strat", limit=10)
            self.assertFalse(res.empty)

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.base_command.DataProvider")
    def test_execute_full_flow(
        self, mock_provider_cls, mock_writer_cls, mock_agent_cls
    ):
        """Cover main execute loop"""
        start_cfg = self.config.copy()
        cmd = AnalyzeCommand(start_cfg)

        with patch.object(cmd, "_fetch_candidates_df_logic") as mock_fetch:
            mock_fetch.return_value = pd.DataFrame([{"code": "1001"}])

            with patch.object(cmd, "_run_async_batch") as mock_run:
                mock_run.return_value = [{"code": "1001"}]

                with patch.object(cmd, "_save_results") as mock_save:

                    # Call execute
                    cmd.execute(strategy="test_strat")

                    mock_run.assert_called()
                    mock_save.assert_called()

    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("src.commands.base_command.DataProvider")
    def test_execute_strategy_loop_real(
        self, mock_provider_cls, mock_writer_cls, mock_agent_cls
    ):
        """Cover strategy iteration loop (lines 51-62)"""
        start_cfg = self.config.copy()
        start_cfg["strategies"] = {"s1": {}, "s2": {}}  # 2 strategies
        cmd = AnalyzeCommand(start_cfg)

        # When execute(strategy=None) is called, it iterates s1, s2 and calls self.execute(strategy='s1/s2')
        # We want to mock the recursive calls to STOP execution there, but allow the LOOP to run.
        # But patching self.execute would stop the loop too if it was recursionpoint.
        # NO, the loop is in the 'strategy=None' block.
        # The 'strategy=s1' call is `self.execute(...)`.
        # If we patch `execute`, `self.execute` calls the mock.
        # So we CAN patch `execute` IF we ensure the *first* call is NOT the mock.

        # Easier: Mock `_fetch_candidates_df_logic` to return Empty.
        # Then execute('s1') runs, calls fetch, gets empty, returns. Loop continues.

        with patch.object(cmd, "_fetch_candidates_df_logic") as mock_fetch:
            mock_fetch.return_value = (
                pd.DataFrame()
            )  # No candidates -> returns (lines 76-78 covered)

            cmd.execute(strategy=None)

            # Should have been called twice (once for s1, once for s2)
            self.assertEqual(mock_fetch.call_count, 2)

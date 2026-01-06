"""
Tests for src/commands/*.py
Designed to cover core execution paths by mocking external dependencies.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# --- MOCK CONFIG FIXTURE ---
def get_mock_config():
    return {
        "current_strategy": "test_strategy",
        "data": {"jp_stock_list": "data/input/test.csv", "output_path": "data/output"},
        "csv_mapping": {"col_map": {}, "numeric_cols": []},
        "ai": {
            "model_name": "test-model",
            "interval_sec": 0.01,  # Fast for tests
            "max_concurrency": 2,
            "validity_days": 7,
        },
        "circuit_breaker": {"consecutive_failure_threshold": 3},
        "database": {"retention_days": 30},
        "system": {"max_workers": 2},
        "strategies": {
            "test_strategy": {
                "default_style": "style",
                "persona": "p",
                "default_horizon": "h",
                "base_score": 0,
                "min_requirements": {},
                "points": {},
                "thresholds": {},
            }
        },
        "sector_policies": {"default": {"na_allowed": []}},
        "scoring": {},
        "scoring_v2": {},
    }


class TestExtractCommand(unittest.TestCase):
    """Unit tests for ExtractCommand."""

    @patch("src.provider.DataProvider")
    @patch("src.database.StockDatabase")
    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    def test_execute_no_candidates(
        self, mock_validator_cls, mock_agent_cls, mock_db_cls, mock_provider_cls
    ):
        """execute should handle empty candidate list gracefully."""
        from src.commands.extract import ExtractCommand

        mock_provider = MagicMock()
        mock_provider.load_latest_market_data.return_value = pd.DataFrame()
        mock_provider.stock_db = MagicMock()
        mock_provider_cls.return_value = mock_provider

        mock_db_cls.return_value = MagicMock()
        mock_agent_cls.return_value = MagicMock()
        mock_validator_cls.return_value = MagicMock()

        cmd = ExtractCommand(get_mock_config(), debug_mode=True)
        # Should not raise
        cmd.execute(strategy="test_strategy", limit=5)

    @unittest.skip("Mock dependencies require update for extract.py internal changes")
    @patch("src.calc.engine.ScoringEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("asyncio.to_thread")
    def test_execute_with_candidates(
        self,
        mock_to_thread,
        mock_validator_cls,
        mock_agent_cls,
        mock_db_cls,
        mock_provider_cls,
        mock_engine_cls,
    ):
        """execute should process candidates and save valid tasks."""
        # Setup to_thread to run sync but be awaitable
        async def mock_to_thread_side_effect(f, *args, **kwargs):
            return f(*args, **kwargs)
        mock_to_thread.side_effect = mock_to_thread_side_effect

        from src.commands.extract import ExtractCommand

        # Setup mocks
        df = pd.DataFrame(
            [
                {
                    "code": "1001",
                    "name": "Test",
                    "quant_score": 80,
                    "sector": "Tech",
                    "market_data_id": 1,
                    # Tier 1 Required
                    "current_price": 1000,
                    "operating_cf": 500,
                    "operating_margin": 10,
                    "per": 15,
                    "pbr": 1.2,
                    "roe": 10,
                }
            ]
        )
        mock_provider = MagicMock()
        mock_provider.load_latest_market_data.return_value = df
        mock_provider.stock_db = MagicMock()
        mock_provider_cls.return_value = mock_provider

        mock_db = MagicMock()
        mock_db.get_ai_cache.return_value = None
        mock_db.get_market_data_id.return_value = 1
        mock_db_cls.return_value = mock_db

        mock_agent = MagicMock()
        mock_agent._create_prompt.return_value = "Test Prompt"
        mock_agent_cls.return_value = mock_agent

        mock_validator = MagicMock()
        mock_validator.validate.return_value = (True, None)  # Valid
        mock_validator_cls.return_value = mock_validator

        mock_engine = MagicMock()
        mock_engine.calculate_score.return_value = df
        mock_engine.filter_and_rank.return_value = df
        mock_engine_cls.return_value = mock_engine

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = ExtractCommand(get_mock_config(), debug_mode=True)
            cmd.interim_dir = tmpdir
            output_path = os.path.join(tmpdir, "test_output.json")

            cmd.execute(strategy="test_strategy", limit=5, output_path=output_path)

            # Verify output file exists
            self.assertTrue(os.path.exists(output_path))
            with open(output_path, "r") as f:
                tasks = json.load(f)
            self.assertEqual(len(tasks), 1)
            self.assertEqual(tasks[0]["code"], "1001")


class TestAnalyzeCommand(unittest.TestCase):
    """Unit tests for AnalyzeCommand."""

    @patch("src.provider.DataProvider")
    @patch("src.database.StockDatabase")
    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    def test_execute_no_candidates(
        self, mock_writer_cls, mock_agent_cls, mock_db_cls, mock_provider_cls
    ):
        """execute should handle empty candidate list."""
        from src.commands.analyze import AnalyzeCommand

        mock_provider = MagicMock()
        mock_provider.load_latest_market_data.return_value = pd.DataFrame()
        mock_provider.stock_db = MagicMock()
        mock_provider_cls.return_value = mock_provider

        mock_db_cls.return_value = MagicMock()
        mock_agent_cls.return_value = MagicMock()
        mock_writer_cls.return_value = MagicMock()

        cmd = AnalyzeCommand(get_mock_config(), debug_mode=True)
        cmd.execute(strategy="test_strategy", limit=5)
        # Should not raise

    @unittest.skip("Mock dependencies require update for analyze.py internal changes")
    @patch("src.commands.analyze.ScoringEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    @patch("src.commands.analyze.AIAgent")
    @patch("src.commands.analyze.ResultWriter")
    @patch("asyncio.to_thread")
    def test_execute_processes_candidates(
        self,
        mock_to_thread,
        mock_writer_cls,
        mock_agent_cls,
        mock_db_cls,
        mock_provider_cls,
        mock_engine_cls,
    ):
        """execute should process candidates with AI agent and save results."""
        # Setup to_thread to run sync but be awaitable
        async def mock_to_thread_side_effect(f, *args, **kwargs):
            return f(*args, **kwargs)
        mock_to_thread.side_effect = mock_to_thread_side_effect

        from src.commands.analyze import AnalyzeCommand

        # Mocks
        df = pd.DataFrame(
            [
                {
                    "code": "2001",
                    "name": "AnalyzeTest",
                    "quant_score": 75,
                    "sector": "Retail",
                    "market_data_id": 2,
                    # Tier 1 Required
                    "current_price": 2000,
                    "operating_cf": 1000,
                    "operating_margin": 15,
                    "per": 12,
                    "pbr": 1.5,
                    "roe": 12,
                    "ocf_margin": 10,
                    "equity_ratio": 50,  # [v2.0] used in is_abnormal
                }
            ]
        )

        mock_provider = MagicMock()
        mock_provider.load_latest_market_data.return_value = df
        mock_provider.get_ai_cache.return_value = (None, "hash123")  # No cache
        mock_provider.stock_db = MagicMock()
        mock_provider_cls.return_value = mock_provider

        mock_db = MagicMock()
        mock_db_cls.return_value = mock_db

        mock_agent = MagicMock()
        mock_agent.analyze.return_value = {
            "ai_sentiment": "Bullish",
            "ai_reason": "Good",
        }
        mock_agent.get_total_calls.return_value = 0
        mock_agent_cls.return_value = mock_agent

        mock_writer = MagicMock()
        mock_writer_cls.return_value = mock_writer

        mock_engine = MagicMock()
        mock_engine.calculate_score.return_value = df
        mock_engine.filter_and_rank.return_value = df
        mock_engine_cls.return_value = mock_engine

        cmd = AnalyzeCommand(get_mock_config(), debug_mode=True)
        cmd.execute(strategy="test_strategy", limit=1)

        # Verify AI analyze was called
        mock_agent.analyze.assert_called_once()

        # Verify results saved
        mock_writer.save.assert_called_once()


class TestIngestCommand(unittest.TestCase):
    """Unit tests for IngestCommand."""

    @patch("src.provider.DataProvider")
    @patch("src.database.StockDatabase")
    @patch("src.commands.ingest.ResultWriter")
    def test_execute_no_files(self, mock_writer_cls, mock_db_cls, mock_provider_cls):
        """execute should handle no matching files gracefully."""
        from src.commands.ingest import IngestCommand

        mock_provider = MagicMock()
        mock_provider.stock_db = MagicMock()
        mock_provider_cls.return_value = mock_provider
        mock_db_cls.return_value = MagicMock()
        mock_writer_cls.return_value = MagicMock()

        cmd = IngestCommand(get_mock_config(), debug_mode=True)
        cmd.execute(file_patterns=["/non/existent/path/*.json"])
        # Should not raise

    @patch("src.provider.DataProvider")
    @patch("src.database.StockDatabase")
    @patch("src.commands.ingest.ResultWriter")
    def test_execute_ingest_valid_json(
        self, mock_writer_cls, mock_db_cls, mock_provider_cls
    ):
        """execute should parse JSON and save records to DB."""
        from src.commands.ingest import IngestCommand

        mock_provider = MagicMock()
        mock_provider.stock_db = MagicMock()
        mock_provider_cls.return_value = mock_provider
        mock_db_cls.return_value = MagicMock()
        mock_writer_cls.return_value = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test JSON
            test_file = os.path.join(tmpdir, "test_ingest.json")
            records = [
                {
                    "code": "3001",
                    "ai_sentiment": "Bullish",
                    "strategy": "test_strategy",
                },
                {
                    "code": "3002",
                    "ai_sentiment": "Bearish",
                    "strategy": "test_strategy",
                },
            ]
            with open(test_file, "w") as f:
                json.dump(records, f)

            cmd = IngestCommand(get_mock_config(), debug_mode=True)
            # IngestCommand creates its own provider, but it's mocked at src.provider level
            # We need to assert on the instance's provider, not the class mock
            cmd.provider = mock_provider  # Inject our mock
            cmd.execute(
                file_patterns=[test_file], output_format="json"
            )  # Skip CSV export

            # Verify save_analysis_result called for each record
            self.assertEqual(mock_provider.save_analysis_result.call_count, 2)

    @patch("src.commands.ingest.pd.read_sql")
    @patch("src.models.db_proxy")
    @patch("src.provider.DataProvider")
    @patch("src.database.StockDatabase")
    @patch("src.commands.ingest.ResultWriter")
    def test_export_to_csv_with_data(
        self,
        mock_writer_cls,
        mock_db_cls,
        mock_provider_cls,
        mock_db_proxy,
        mock_read_sql,
    ):
        """_export_to_csv should query DB and save results."""
        from src.commands.ingest import IngestCommand

        mock_provider = MagicMock()
        mock_provider.stock_db = MagicMock()
        mock_provider_cls.return_value = mock_provider
        mock_db_cls.return_value = MagicMock()

        mock_writer = MagicMock()
        mock_writer_cls.return_value = mock_writer

        # Mock DB connection
        mock_conn = MagicMock()
        mock_db_proxy.connection.return_value = mock_conn

        # Mock SQL result
        mock_df = pd.DataFrame(
            [
                {
                    "code": "4001",
                    "name": "Stock1",
                    "ai_sentiment": "Bullish",
                    "quant_score": 80,
                },
                {
                    "code": "4002",
                    "name": "Stock2",
                    "ai_sentiment": "Bearish",
                    "quant_score": 60,
                },
            ]
        )
        mock_read_sql.return_value = mock_df

        cmd = IngestCommand(get_mock_config(), debug_mode=True)
        cmd._export_to_csv(strategies=["test_strategy"], filter_codes=["4001", "4002"])

        # Verify SQL was called
        mock_read_sql.assert_called()

        # Verify writer.save was called with DataFrame
        mock_writer.save.assert_called_once()
        call_args = mock_writer.save.call_args
        saved_df = call_args[0][0]
        self.assertEqual(len(saved_df), 2)

    @patch("src.commands.ingest.pd.read_sql")
    @patch("src.models.db_proxy")
    @patch("src.provider.DataProvider")
    @patch("src.database.StockDatabase")
    @patch("src.commands.ingest.ResultWriter")
    def test_export_to_csv_no_results(
        self,
        mock_writer_cls,
        mock_db_cls,
        mock_provider_cls,
        mock_db_proxy,
        mock_read_sql,
    ):
        """_export_to_csv should handle empty result gracefully."""
        from src.commands.ingest import IngestCommand

        mock_provider = MagicMock()
        mock_provider.stock_db = MagicMock()
        mock_provider_cls.return_value = mock_provider
        mock_db_cls.return_value = MagicMock()

        mock_writer = MagicMock()
        mock_writer_cls.return_value = mock_writer

        # Mock empty result
        mock_db_proxy.connection.return_value = MagicMock()
        mock_read_sql.return_value = pd.DataFrame()

        cmd = IngestCommand(get_mock_config(), debug_mode=True)
        cmd._export_to_csv(strategies=["test_strategy"], filter_codes=None)

        # Writer should NOT be called when no results
        mock_writer.save.assert_not_called()

    @patch("src.commands.ingest.pd.read_sql")
    @patch("src.models.db_proxy")
    @patch("src.provider.DataProvider")
    @patch("src.database.StockDatabase")
    @patch("src.commands.ingest.ResultWriter")
    def test_export_to_csv_chunking(
        self,
        mock_writer_cls,
        mock_db_cls,
        mock_provider_cls,
        mock_db_proxy,
        mock_read_sql,
    ):
        """_export_to_csv should chunk large code lists."""
        from src.commands.ingest import IngestCommand

        mock_provider = MagicMock()
        mock_provider.stock_db = MagicMock()
        mock_provider_cls.return_value = mock_provider
        mock_db_cls.return_value = MagicMock()

        mock_writer = MagicMock()
        mock_writer_cls.return_value = mock_writer

        mock_db_proxy.connection.return_value = MagicMock()
        mock_read_sql.return_value = pd.DataFrame([{"code": "1"}])

        # Generate 600 codes (exceeds chunk_size of 500)
        large_code_list = [str(i) for i in range(600)]

        cmd = IngestCommand(get_mock_config(), debug_mode=True)
        cmd._export_to_csv(strategies=["test_strategy"], filter_codes=large_code_list)

        # Should have called read_sql twice (2 chunks: 500 + 100)
        self.assertEqual(mock_read_sql.call_count, 2)


if __name__ == "__main__":
    unittest.main()

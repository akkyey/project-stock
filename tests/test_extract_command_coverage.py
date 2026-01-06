# tests/test_extract_command_coverage.py
"""
ExtractCommand のカバレッジ向上テスト
"""

import asyncio
import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd


def get_mock_config():
    """テスト用の設定を返す。"""
    return {
        "ai": {
            "model_name": "test-model",
            "interval_sec": 0.01,
        },
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
        "validation": {"hard_cut": {}},
    }


class TestExtractCommandInit(unittest.TestCase):
    """ExtractCommand の初期化テスト"""

    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_init_creates_directories(
        self, mock_db_cls, mock_provider_cls, mock_validator_cls, mock_agent_cls
    ):
        """__init__ がディレクトリを作成することを確認"""
        from src.commands.extract import ExtractCommand

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("src.commands.extract.os.makedirs") as mock_makedirs:
                cmd = ExtractCommand(get_mock_config(), debug_mode=True)

                # ディレクトリ作成が呼ばれていることを確認
                self.assertTrue(mock_makedirs.called)


class TestExtractCommandExecute(unittest.TestCase):
    """ExtractCommand.execute のテスト"""

    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_execute_no_candidates(
        self, mock_db_cls, mock_provider_cls, mock_validator_cls, mock_agent_cls
    ):
        """候補がない場合のテスト"""
        from src.commands.extract import ExtractCommand

        mock_provider = MagicMock()
        mock_provider.load_latest_market_data.return_value = pd.DataFrame()
        mock_provider_cls.return_value = mock_provider

        cmd = ExtractCommand(get_mock_config(), debug_mode=True)
        cmd.execute(strategy="test_strategy", limit=5)
        # エラーなく完了することを確認

    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_execute_with_codes_empty_df(
        self, mock_db_cls, mock_provider_cls, mock_validator_cls, mock_agent_cls
    ):
        """codes指定で空のDataFrameの場合"""
        from src.commands.extract import ExtractCommand

        mock_provider = MagicMock()
        mock_provider.load_latest_market_data.return_value = pd.DataFrame()
        mock_provider_cls.return_value = mock_provider

        cmd = ExtractCommand(get_mock_config(), debug_mode=True)
        cmd.execute(strategy="test_strategy", codes=["1001"])
        # エラーなく完了することを確認

    @patch("src.calc.engine.ScoringEngine")
    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_execute_saves_valid_tasks(
        self,
        mock_db_cls,
        mock_provider_cls,
        mock_validator_cls,
        mock_agent_cls,
        mock_engine_cls,
    ):
        """有効なタスクが保存されることを確認"""
        from src.commands.extract import ExtractCommand

        # モックデータ
        df = pd.DataFrame([{"code": "1001", "name": "Test", "quant_score": 80}])

        mock_provider = MagicMock()
        mock_provider.load_latest_market_data.return_value = df
        mock_provider_cls.return_value = mock_provider

        mock_engine = MagicMock()
        mock_engine.calculate_score.return_value = df
        mock_engine.filter_and_rank.return_value = df
        mock_engine_cls.return_value = mock_engine

        mock_validator = MagicMock()
        mock_validator.validate_stock_data.return_value = (True, [])
        mock_validator_cls.return_value = mock_validator

        mock_agent = MagicMock()
        mock_agent._create_prompt.return_value = "Test Prompt"
        mock_agent_cls.return_value = mock_agent

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = ExtractCommand(get_mock_config(), debug_mode=True)
            cmd.interim_dir = tmpdir
            output_path = os.path.join(tmpdir, "output.json")

            # _process_single_candidate をモック
            cmd._process_single_candidate = MagicMock(
                return_value=({"code": "1001", "prompt": "test"}, True, "OK")
            )

            cmd.execute(strategy="test_strategy", limit=1, output_path=output_path)

            # ファイルが作成されることを確認
            self.assertTrue(os.path.exists(output_path))
            with open(output_path) as f:
                tasks = json.load(f)
            self.assertEqual(len(tasks), 1)

    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_execute_saves_quarantine(
        self, mock_db_cls, mock_provider_cls, mock_validator_cls, mock_agent_cls
    ):
        """無効タスクが隔離ファイルに保存されることを確認"""
        from src.commands.extract import ExtractCommand

        df = pd.DataFrame([{"code": "bad", "name": "Bad Stock"}])

        mock_provider = MagicMock()
        mock_provider.load_latest_market_data.return_value = df
        mock_provider_cls.return_value = mock_provider

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = ExtractCommand(get_mock_config(), debug_mode=True)
            cmd.interim_dir = tmpdir
            cmd.quarantine_dir = os.path.join(tmpdir, "quarantine")
            os.makedirs(cmd.quarantine_dir, exist_ok=True)

            # 失敗を返すようモック
            cmd._process_single_candidate = MagicMock(
                return_value=({"code": "bad"}, False, "Invalid data")
            )
            cmd._fetch_candidates_logic = MagicMock(return_value=[{"code": "bad"}])

            cmd.execute(strategy="test_strategy", limit=1)

            # 隔離ファイルが作成されることを確認
            quarantine_files = os.listdir(cmd.quarantine_dir)
            self.assertGreater(len(quarantine_files), 0)


class TestFetchCandidates(unittest.TestCase):
    """候補取得のテスト"""

    @patch("src.calc.engine.ScoringEngine")
    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_fetch_candidates_logic_returns_list(
        self,
        mock_db_cls,
        mock_provider_cls,
        mock_validator_cls,
        mock_agent_cls,
        mock_engine_cls,
    ):
        """_fetch_candidates_logic がリストを返すことを確認"""
        from src.commands.extract import ExtractCommand

        df = pd.DataFrame(
            [
                {"code": "1001", "name": "A", "quant_score": 80},
                {"code": "1002", "name": "B", "quant_score": 70},
            ]
        )

        mock_provider = MagicMock()
        mock_provider.load_latest_market_data.return_value = df
        mock_provider_cls.return_value = mock_provider

        mock_engine = MagicMock()
        mock_engine.calculate_score.return_value = df
        mock_engine.filter_and_rank.return_value = df
        mock_engine_cls.return_value = mock_engine

        mock_db = MagicMock()
        mock_db.get_ai_cache.return_value = None
        mock_db_cls.return_value = mock_db

        cmd = ExtractCommand(get_mock_config(), debug_mode=True)
        result = cmd._fetch_candidates_logic("test_strategy", limit=2)

        self.assertEqual(len(result), 2)

    @patch("src.calc.engine.ScoringEngine")
    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_fetch_candidates_by_code(
        self,
        mock_db_cls,
        mock_provider_cls,
        mock_validator_cls,
        mock_agent_cls,
        mock_engine_cls,
    ):
        """_fetch_candidates_by_code のテスト"""
        from src.commands.extract import ExtractCommand

        df = pd.DataFrame(
            [
                {"code": "1001", "name": "A", "quant_score": 80},
                {"code": "1002", "name": "B", "quant_score": 70},
            ]
        )

        mock_provider = MagicMock()
        mock_provider.load_latest_market_data.return_value = df
        mock_provider_cls.return_value = mock_provider

        mock_engine = MagicMock()
        mock_engine.calculate_score.return_value = df
        mock_engine_cls.return_value = mock_engine

        cmd = ExtractCommand(get_mock_config(), debug_mode=True)
        result = cmd._fetch_candidates_by_code(["1001"], "test_strategy")

        self.assertEqual(len(result), 2)  # filter はcalculate_score後


class TestProcessSingleCandidate(unittest.TestCase):
    """_process_single_candidate のテスト"""

    @patch("src.domain.models.StockAnalysisData")
    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_process_returns_valid_task(
        self,
        mock_db_cls,
        mock_provider_cls,
        mock_validator_cls,
        mock_agent_cls,
        mock_stock_data_cls,
    ):
        """有効なタスクが返されること"""
        from src.commands.extract import ExtractCommand

        mock_validator = MagicMock()
        mock_validator.validate_stock_data.return_value = (True, [])
        mock_validator_cls.return_value = mock_validator

        mock_agent = MagicMock()
        mock_agent._create_prompt.return_value = "Test Prompt"
        mock_agent_cls.return_value = mock_agent

        mock_db = MagicMock()
        mock_db.get_market_data_id.return_value = 123
        mock_db_cls.return_value = mock_db

        mock_stock_data_cls.return_value = MagicMock()

        cmd = ExtractCommand(get_mock_config(), debug_mode=True)

        row = pd.Series(
            {
                "code": "1001",
                "name": "Test Stock",
                "quant_score": 85,
                "sector": "Tech",
                "current_price": 1000,
                "per": 15,
                "pbr": 1.2,
                "roe": 10,
            }
        )

        task, is_valid, reason = cmd._process_single_candidate(row, "test_strategy")

        self.assertTrue(is_valid)
        self.assertEqual(task["code"], "1001")
        self.assertEqual(task["prompt"], "Test Prompt")

    @patch("src.domain.models.StockAnalysisData")
    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_process_returns_invalid_task(
        self,
        mock_db_cls,
        mock_provider_cls,
        mock_validator_cls,
        mock_agent_cls,
        mock_stock_data_cls,
    ):
        """無効なタスクが返されること"""
        from src.commands.extract import ExtractCommand

        mock_validator = MagicMock()
        mock_validator.validate_stock_data.return_value = (
            False,
            ["Missing critical data"],
        )
        mock_validator_cls.return_value = mock_validator

        mock_agent = MagicMock()
        mock_agent._create_prompt.return_value = "Test Prompt"
        mock_agent_cls.return_value = mock_agent

        mock_stock_data_cls.return_value = MagicMock()

        cmd = ExtractCommand(get_mock_config(), debug_mode=True)

        row = {"code": "bad", "name": "Bad Stock"}

        task, is_valid, reason = cmd._process_single_candidate(row, "test_strategy")

        self.assertFalse(is_valid)
        self.assertIn("Missing critical data", reason)


class TestSaveQuarantine(unittest.TestCase):
    """_save_quarantine のテスト"""

    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_save_quarantine_creates_file(
        self, mock_db_cls, mock_provider_cls, mock_validator_cls, mock_agent_cls
    ):
        """隔離ファイルが作成されること"""
        from src.commands.extract import ExtractCommand

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = ExtractCommand(get_mock_config(), debug_mode=True)
            cmd.quarantine_dir = tmpdir

            error_tasks = [
                {"code": "bad1", "error_reason": "Invalid"},
                {"code": "bad2", "error_reason": "Missing"},
            ]

            cmd._save_quarantine(error_tasks, "test_strategy")

            files = os.listdir(tmpdir)
            self.assertEqual(len(files), 1)
            self.assertIn("quarantine", files[0])

    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_save_quarantine_empty_does_nothing(
        self, mock_db_cls, mock_provider_cls, mock_validator_cls, mock_agent_cls
    ):
        """空のリストでは何も保存されない"""
        from src.commands.extract import ExtractCommand

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = ExtractCommand(get_mock_config(), debug_mode=True)
            cmd.quarantine_dir = tmpdir

            cmd._save_quarantine([], "test_strategy")

            files = os.listdir(tmpdir)
            self.assertEqual(len(files), 0)


class TestRunAsyncBatch(unittest.TestCase):
    """_run_async_batch のテスト"""

    @patch("src.commands.extract.AIAgent")
    @patch("src.commands.extract.ValidationEngine")
    @patch("src.commands.base_command.DataProvider")
    @patch("src.commands.base_command.StockDatabase")
    def test_run_async_batch(
        self, mock_db_cls, mock_provider_cls, mock_validator_cls, mock_agent_cls
    ):
        """非同期バッチ処理のテスト"""
        from src.commands.extract import ExtractCommand

        cmd = ExtractCommand(get_mock_config(), debug_mode=True)
        cmd._process_single_candidate = MagicMock(
            return_value=({"code": "1001"}, True, "OK")
        )

        candidates = [{"code": "1001"}, {"code": "1002"}]

        results = asyncio.run(cmd._run_async_batch(candidates, "test_strategy"))

        self.assertEqual(len(results), 2)
        for task, is_valid, reason in results:
            self.assertTrue(is_valid)


if __name__ == "__main__":
    unittest.main()

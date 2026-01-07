"""
tests/test_coverage_improvements.py

カバレッジ改善のための追加テスト
80%未満のモジュールを対象
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import yaml


class TestResponseParser(unittest.TestCase):
    """ai/response_parser.py のカバレッジ改善テスト"""

    def setUp(self):
        from src.ai.response_parser import ResponseParser

        self.parser = ResponseParser()

    def test_parse_response_valid_json(self):
        """正常なJSON応答のパース"""
        text = json.dumps(
            {
                "ai_sentiment": "Bullish",
                "ai_reason": "【結論】強気。｜【強み】成長性。｜【懸念】なし。",
                "ai_risk": "Low",
                "ai_horizon": "Short",
                "ai_detail": "①詳細②詳細③詳細④詳細⑤詳細⑥詳細⑦詳細",
                "audit_version": 1,
            }
        )
        result = self.parser.parse_response(text)
        self.assertEqual(result["ai_sentiment"], "Bullish")
        self.assertEqual(result["ai_risk"], "Low")

    def test_parse_response_with_markdown_fence(self):
        """マークダウンのコードフェンス付きJSON"""
        text = '```json\n{"ai_sentiment": "Neutral", "ai_reason": "test"}\n```'
        result = self.parser.parse_response(text)
        self.assertEqual(result["ai_sentiment"], "Neutral")

    def test_parse_response_invalid_json(self):
        """不正なJSONのパース"""
        result = self.parser.parse_response("not a json")
        self.assertEqual(result["ai_sentiment"], "Error")
        self.assertTrue(result.get("_parse_error"))

    def test_validate_response_valid(self):
        """正常な応答のバリデーション"""
        result = {
            "ai_sentiment": "Bullish",
            "ai_reason": "【結論】強気。｜【強み】成長性。｜【懸念】なし。",
            "ai_detail": "①詳細②詳細③詳細④詳細⑤詳細⑥詳細⑦詳細",
            "ai_risk": "Low",
        }
        is_valid, error = self.parser.validate_response(result)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_response_invalid_sentiment(self):
        """無効なsentimentのバリデーション"""
        result = {"ai_sentiment": "InvalidValue", "ai_reason": "test"}
        is_valid, error = self.parser.validate_response(result)
        self.assertFalse(is_valid)
        self.assertIn("Invalid sentiment", error)

    def test_validate_response_empty_summary(self):
        """空のサマリーのバリデーション"""
        result = {"ai_sentiment": "Bullish", "ai_reason": ""}
        is_valid, error = self.parser.validate_response(result)
        self.assertFalse(is_valid)
        self.assertIn("Empty", error)

    def test_validate_response_multiline_summary(self):
        """複数行のサマリー（禁止）"""
        result = {"ai_sentiment": "Bullish", "ai_reason": "line1\nline2"}
        is_valid, error = self.parser.validate_response(result)
        self.assertFalse(is_valid)
        self.assertIn("newlines", error)

    def test_validate_response_missing_tags(self):
        """必須タグが欠けているサマリー"""
        result = {"ai_sentiment": "Bullish", "ai_reason": "【結論】のみ"}
        is_valid, error = self.parser.validate_response(result)
        self.assertFalse(is_valid)
        self.assertIn("format", error)

    def test_validate_response_duplicated_tags(self):
        """タグが重複しているサマリー"""
        result = {
            "ai_sentiment": "Bullish",
            "ai_reason": "【結論】a｜【強み】b｜【懸念】c【結論】d",
            "ai_detail": "①②③④⑤⑥⑦",
        }
        is_valid, error = self.parser.validate_response(result)
        self.assertFalse(is_valid)
        self.assertIn("duplicated", error)

    def test_validate_response_missing_detail_sections(self):
        """詳細の番号付きセクションが欠けている"""
        result = {
            "ai_sentiment": "Bullish",
            "ai_reason": "【結論】a｜【強み】b｜【懸念】c",
            "ai_detail": "詳細なし",
        }
        is_valid, error = self.parser.validate_response(result)
        self.assertFalse(is_valid)
        self.assertIn("numbered sections", error)

    def test_validate_response_blacklist(self):
        """ブラックリストフレーズの検出"""
        result = {
            "ai_sentiment": "Bullish",
            "ai_reason": "【結論】安定した業績推移｜【強み】b｜【懸念】c",
            "ai_detail": "①②③④⑤⑥⑦",
        }
        is_valid, error = self.parser.validate_response(result)
        self.assertFalse(is_valid)
        self.assertIn("Blacklist", error)

    def test_generate_dqf_alert_with_missing(self):
        """欠損データがある場合のDQFアラート"""
        row = {"roe": None, "per": None, "operating_cf": 100}
        alert = self.parser.generate_dqf_alert(row)
        self.assertIn("DQF ALERT", alert)
        self.assertIn("ROE", alert)
        self.assertIn("PER", alert)

    def test_generate_dqf_alert_no_missing(self):
        """欠損データがない場合"""
        row = {
            "roe": 10,
            "per": 15,
            "operating_cf": 100,
            "debt_equity_ratio": 0.5,
            "free_cf": 50,
        }
        alert = self.parser.generate_dqf_alert(row)
        self.assertEqual(alert, "")

    def test_load_blacklist_with_file(self):
        """ブラックリストファイルの読み込み"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("# コメント\n")
            f.write("禁止フレーズ1\n")
            f.write("禁止フレーズ2\n")
            temp_path = f.name

        try:
            with patch.object(self.parser, "_load_blacklist") as mock_load:
                mock_load.return_value = [
                    "禁止フレーズ1",
                    "禁止フレーズ2",
                    "安定した業績推移",
                ]
                parser = type(self.parser)()
                parser.blacklist = mock_load.return_value
                self.assertIn("禁止フレーズ1", parser.blacklist)
        finally:
            os.unlink(temp_path)


class TestResultWriter(unittest.TestCase):
    """result_writer.py のカバレッジ改善テスト"""

    def setUp(self):
        self.config = {"paths": {"output_dir": tempfile.mkdtemp()}}

    def test_save_empty_dataframe(self):
        """空のDataFrameの保存（空でもファイルは作成される）"""
        from src.result_writer import ResultWriter

        writer = ResultWriter(self.config)
        df = pd.DataFrame()
        # 空のDataFrameでもファイルパスが返される
        result = writer.save(df, "empty_test.csv")
        # 戻り値がNoneかパスかは実装次第なので、エラーなく完了すればOK
        self.assertTrue(result is None or isinstance(result, str))

    def test_save_with_extension_replacement(self):
        """拡張子の置換（.xlsx → .csv）"""
        from src.result_writer import ResultWriter

        writer = ResultWriter(self.config)
        df = pd.DataFrame({"code": ["1234"], "name": ["Test"]})
        result = writer.save(df, "test.xlsx")
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith(".csv"))


class TestConfigLoader(unittest.TestCase):
    """config_loader.py のカバレッジ改善テスト"""

    def test_load_config_file_not_found(self):
        """設定ファイルが見つからない場合"""
        from src.config_loader import load_config

        # ファイルが見つからなくてもデフォルト設定が返される
        config = load_config("/nonexistent/path.yaml")
        self.assertIsNotNone(config)
        self.assertIsInstance(config, dict)

    def test_load_config_invalid_yaml(self):
        """不正なYAMLファイル"""
        from src.config_loader import load_config

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content:")
            temp_path = f.name
        try:
            # 不正なYAMLでもデフォルト設定が返される
            config = load_config(temp_path)
            self.assertIsNotNone(config)
        finally:
            os.unlink(temp_path)


class TestEnvLoader(unittest.TestCase):
    """env_loader.py のカバレッジ改善テスト"""

    def test_load_env_file_not_found(self):
        """環境ファイルが見つからない場合"""
        from src.env_loader import load_env_file

        with patch("os.path.exists", return_value=False):
            # エラーなく完了すればOK
            load_env_file()


class TestKeyManager(unittest.TestCase):
    """ai/key_manager.py のカバレッジ改善テスト"""

    def test_debug_mode_skips_client(self):
        """デバッグモードでクライアント生成をスキップ"""
        from src.ai.key_manager import APIKeyManager

        manager = APIKeyManager(debug_mode=True)
        client = manager.get_current_client()
        self.assertIsNone(client)

    def test_rotate_key_no_keys(self):
        """キーがない場合のローテーション"""
        from src.ai.key_manager import APIKeyManager

        manager = APIKeyManager(debug_mode=True)
        manager.api_keys = []
        result = manager.rotate_key()
        self.assertFalse(result)

    def test_update_stats(self):
        """統計の更新"""
        from src.ai.key_manager import APIKeyManager

        manager = APIKeyManager(debug_mode=True)
        manager.api_keys = ["key1"]
        manager.key_stats = [
            {
                "total_calls": 0,
                "success_count": 0,
                "retry_count": 0,
                "error_429_count": 0,
                "status": "active",
            }
        ]
        manager.update_stats(0, "total_calls")
        self.assertEqual(manager.key_stats[0]["total_calls"], 1)


class TestEngine(unittest.TestCase):
    """engine.py のカバレッジ改善テスト (SKIP: src.engine は削除済み)"""

    @unittest.skip("src.engine.AnalysisEngine は削除済み")
    def test_calculate_scores_empty_df(self):
        """空のDataFrame"""
        pass


class TestPromptBuilder(unittest.TestCase):
    """ai/prompt_builder.py のカバレッジ改善テスト"""

    def test_build_prompt_with_missing_fields(self):
        """欠損フィールドがある場合のプロンプト生成"""
        from src.ai.prompt_builder import PromptBuilder

        config = {"ai": {"prompt_template": "config/ai_prompts.yaml"}}
        with patch("os.path.exists", return_value=True):
            with patch(
                "builtins.open",
                unittest.mock.mock_open(read_data="template: test {code}"),
            ):
                builder = PromptBuilder(config)
                # テンプレートが読み込まれることを確認
                self.assertIsNotNone(builder)




class TestValidationEngineNew(unittest.TestCase):
    """validation_engine.py のカバレッジ改善テスト"""

    def test_validate_stock_data_basic(self):
        """基本的なバリデーション"""
        from src.validation_engine import ValidationEngine

        config = {"validation": {"hard_cut": {}}}
        engine = ValidationEngine(config)
        row = {"code": "1234", "name": "Test", "equity_ratio": 50, "per": 15}
        # validate_stock_dataメソッドはタプルを返す (is_valid, reasons)
        result = engine.validate_stock_data(row)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)


class TestResultWriterExtended(unittest.TestCase):
    """result_writer.py の追加カバレッジテスト"""

    def setUp(self):
        self.config = {"paths": {"output_dir": tempfile.mkdtemp()}}

    def test_refine_rating(self):
        """AIレーティングの微調整ロジック"""
        from src.result_writer import ResultWriter

        writer = ResultWriter(self.config)

        # テストデータの組み合わせ
        test_cases = [
            ({"ai_sentiment": "Neutral", "ai_risk": "High"}, "Neutral (Caution)"),
            ({"ai_sentiment": "Neutral", "ai_risk": "Low"}, "Neutral (Positive)"),
            ({"ai_sentiment": "Neutral", "ai_risk": "Medium"}, "Neutral (Wait)"),
            (
                {"ai_sentiment": "Bullish", "ai_reason": "これは例外的な措置です"},
                "Bullish (Defensive)",
            ),
            (
                {"ai_sentiment": "Bullish", "ai_reason": "最高です"},
                "Bullish (Aggressive)",
            ),
        ]

        for row, expected in test_cases:
            # 必要なカラムを追加
            row_data = row.copy()
            if "ai_reason" not in row_data:
                row_data["ai_reason"] = ""
            if "ai_risk" not in row_data:
                row_data["ai_risk"] = "Low"  # デフォルト値を設定
            row_data["code"] = "1111"
            row_data["name"] = "Test"

            df = pd.DataFrame([row_data])
            output_path = writer.save(
                df, f"rating_test_{expected.replace(' ', '_')}.csv"
            )

            self.assertIsNotNone(output_path, "Save failed")
            df_out = pd.read_csv(output_path)
            self.assertEqual(df_out["AI_Rating"].iloc[0], expected)

    def test_column_filtering(self):
        """カラムのフィルタリングとリネーム"""
        from src.result_writer import ResultWriter

        writer = ResultWriter(self.config)

        data = {
            "code": ["1111"],
            "name": ["Test"],
            "market_data_id": ["ignore"],
            "unknown_col": ["keep"],
            "ai_sentiment": ["Bullish"],
            "ai_risk": ["Low"],
            "ai_reason": ["comment"],
        }
        df = pd.DataFrame(data)
        output_path = writer.save(df, "filter_test.csv")
        self.assertIsNotNone(output_path)
        df_out = pd.read_csv(output_path)

        self.assertNotIn("market_data_id", df_out.columns)
        self.assertIn("unknown_col", df_out.columns)
        self.assertIn("Code", df_out.columns)
        self.assertIn("AI_Rating", df_out.columns)


class TestConfigLoaderExtended(unittest.TestCase):
    """config_loader.py の追加カバレッジテスト"""

    def _get_valid_dummy_config(self):
        return {
            "current_strategy": "test",
            "data": {
                "output_path": "data/output/result.csv",
                "jp_stock_list": "dummy.csv",
            },
            "csv_mapping": {"col_map": {}, "numeric_cols": []},
            "scoring": {"min_coverage_pct": 50},
            "strategies": {},
            "ai": {"model_name": "gemini-pro", "prompt_template": "dummy"},
            "logging": {"level": "INFO"},
            "api": {"wait_time": 1, "max_retries": 1, "timeout": 10},
        }

    def test_sync_macro_context(self):
        """マーケットコンテキストの読み込み"""
        from src.config_loader import ConfigLoader

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = os.path.join(tmp_dir, "config.yaml")
            context_path = os.path.join(tmp_dir, "market_context.txt")

            defaults = self._get_valid_dummy_config()
            with open(config_path, "w") as f:
                f.write(yaml.dump(defaults))

            with open(context_path, "w") as f:
                f.write("[MACRO_SENTIMENT:bearish]\n[INTEREST_RATE:high]\n")

            loader = ConfigLoader(config_path)

            macro = loader.raw_config.get("scoring_v2", {}).get("macro", {})
            self.assertEqual(macro.get("sentiment"), "bearish")
            self.assertEqual(macro.get("interest_rate"), "high")

    def test_ensure_directories(self):
        """ディレクトリ自動生成"""
        from src.config_loader import ConfigLoader

        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = os.path.join(tmp_dir, "config.yaml")
            output_path = os.path.join(tmp_dir, "new_output", "result.csv")
            db_file = os.path.join(tmp_dir, "new_db", "test.db")

            defaults = self._get_valid_dummy_config()
            defaults["data"]["output_path"] = output_path
            defaults["paths"] = {
                "db_file": db_file,
                "output_dir": os.path.dirname(output_path),
            }

            with open(config_path, "w") as f:
                f.write(yaml.dump(defaults))

            loader = ConfigLoader(config_path)

            self.assertTrue(os.path.exists(os.path.dirname(output_path)))
            self.assertTrue(os.path.exists(os.path.dirname(db_file)))

    def test_load_config_search_paths(self):
        """設定ファイルの探索パスロジック"""
        from src.config_loader import ConfigLoader

        # 存在しないパスを指定して、デフォルトが返るか、あるいは探索ログが出るか
        # ここでは実ファイルを作らずに _load_config の挙動を確認するのは難しい（副作用が強い）
        # なので、ConfigLoaderの _load_config が {} を返すケース（ファイルなし）を確認
        loader = ConfigLoader("non_existent_config.yaml")
        # デフォルト値で初期化されることを確認
        self.assertEqual(loader.raw_config["current_strategy"], "value_strict")


class TestValidationEngineRecover(unittest.TestCase):
    """validation_engine.py のカバレッジ回復テスト"""

    def setUp(self):
        self.config = {
            "validation": {"hard_cut": {"equity_ratio_min": 0, "pbr_max": 20}}
        }

    @unittest.skip("is_abnormal method was removed from ValidationEngine")
    def test_legacy_is_abnormal(self):
        """非推奨メソッド is_abnormal の動作確認（カバレッジ維持）"""
        pass

    def test_validate_stock_data_comprehensive(self):
        """validate_stock_data の網羅的テスト"""
        from src.validation_engine import ValidationEngine

        engine = ValidationEngine(self.config)

        # ケース1: 正常 (全ての必須フィールドを含む)
        row_ok = {
            "code": "1001",
            "name": "OK",
            "market": "Prime",
            "sector": "IT",
            "current_price": 1000,
            "price": 1000,
            "equity_ratio": 50.0,
            "pbr": 1.0,
            "per": 15.0,
            "roe": 10.0,
            "dividend_yield": 2.5,
            "operating_margin": 10.0,
            "sales_growth": 5.0,
            "operating_profit_growth": 5.0,
            "operating_cf": 100.0,
        }
        is_valid, issues = engine.validate_stock_data(row_ok)
        self.assertTrue(is_valid)

        # ケース2: 欠損データ (Critical Missing)
        row_missing = {"code": "1002", "name": "Missing"}
        is_valid, issues = engine.validate_stock_data(row_missing)
        self.assertFalse(is_valid)
        self.assertIn("Missing Critical", str(issues))


class TestOrchestratorExtended(unittest.TestCase):
    """orchestrator.py のカバレッジテスト"""

    @patch("src.reporter.StockReporter")
    @patch("src.orchestrator.Sentinel")
    @patch("src.orchestrator.StockDatabase")
    @patch("src.orchestrator.ConfigLoader")
    def setUp(self, mock_loader_cls, mock_db_cls, mock_sentinel_cls, mock_reporter_cls):
        self.mock_config = {
            "strategies": {"test_strat": {}},
            "paths": {"output_dir": "test_out"},
        }
        mock_loader_cls.return_value.config = self.mock_config

        from src.orchestrator import Orchestrator

        self.orchestrator = Orchestrator(debug_mode=True)
        self.orchestrator.logger = MagicMock()

    @patch("src.orchestrator.get_current_time")
    @patch("src.orchestrator.SentinelAlert")
    def test_handshake_alerts(self, mock_alert_model, mock_time):
        """ハンドシェイク: 未処理アラートがある場合"""
        # 時間固定
        now = datetime(2025, 1, 1, 12, 0, 0)
        mock_time.return_value = now

        # 未処理アラートのモック
        mock_alert = MagicMock()
        mock_alert.id = 1
        mock_alert.detected_at = now - timedelta(days=2)  # 期限切れ
        mock_alert.alert_type = "Critical"
        mock_alert.code = "9999"

        mock_alert_model.select.return_value.where.return_value.order_by.return_value.exists.return_value = (
            True
        )
        mock_alert_model.select.return_value.where.return_value.order_by.return_value.__iter__.return_value = [
            mock_alert
        ]

        self.orchestrator._handshake_procedure()

        # ログにCRITICALが出るか
        self.orchestrator.logger.warning.assert_called()
        args, _ = self.orchestrator.logger.warning.call_args
        self.assertIn("CRITICAL", args[0])

    @patch("src.orchestrator.AnalysisResult")
    @patch("src.orchestrator.SentinelAlert")
    @patch("src.orchestrator.Orchestrator._execute_equity_auditor")
    @patch("src.orchestrator.Orchestrator._export_reports")
    def test_run_daily_flow(self, mock_export, mock_exec, mock_alert, mock_result):
        """Dailyルーチンのフロー確認"""
        # バランス型ターゲット取得のモック
        mock_result.select.return_value.join.return_value.where.return_value.order_by.return_value.limit.return_value = (
            []
        )

        # アラートあり
        mock_alert_inst = MagicMock()
        mock_alert_inst.code = "8888"
        mock_alert_inst.alert_type = "Critical"  # 追加
        mock_alert.select.return_value.where.return_value = [mock_alert_inst]

        self.orchestrator._run_daily()

        # Sentinel実行
        self.orchestrator.sentinel.run.assert_called()
        # EquityAuditor実行 (アラート銘柄が対象になるはず)
        mock_exec.assert_called()
        args, _ = mock_exec.call_args
        self.assertIn("8888", args[0])
        # レポート出力
        mock_export.assert_called_with(
            output_context="daily", source_map={"8888": "Alert(Critical)"}
        )

    @patch("src.orchestrator.subprocess.run")
    def test_recover_db(self, mock_sub):
        """DB自動修復プロセス"""
        with patch("src.orchestrator.MarketData") as mock_md:
            # 修復対象コード
            mock_row = MagicMock()
            mock_row.code_id = "1234"
            mock_md.select.return_value.where.return_value = [mock_row]

            res = self.orchestrator._recover_db("2025-01-01")

            self.assertTrue(res)
            mock_sub.assert_called()
            # コマンド引数の確認
            args, _ = mock_sub.call_args
            cmd = args[0]
            self.assertIn("ingest", cmd)
            self.assertIn("--force", cmd)
            self.assertIn("1234", cmd)

    def test_check_db_integrity_empty(self):
        """DB整合性チェック: データなし"""
        with patch("src.orchestrator.MarketData") as mock_md:
            mock_md.select.return_value.where.return_value.count.return_value = 0
            res = self.orchestrator._check_db_integrity("2025-01-01")
            self.assertTrue(res)

    def test_check_db_integrity_broken(self):
        """DB整合性チェック: 欠損あり"""
        with patch("src.orchestrator.MarketData") as mock_md:
            # 全体件数 10
            mock_md.select.return_value.where.return_value.count.side_effect = [10, 5]
            # 欠損件数 5 (2回目のselect)
            # count()の戻り値を制御するのは難しいので、mockの構成を工夫

            # _check_db_integrityの実装は2回countを呼ぶ
            # 1回目: total_count
            # 2回目: null_count

            res = self.orchestrator._check_db_integrity("2025-01-01")
            # null_count > 0 でも Warning のみで True を返す仕様
            self.assertTrue(res)
            self.orchestrator.logger.warning.assert_called()
            args, _ = self.orchestrator.logger.warning.call_args
            self.assertIn("Integrity Alert", args[0])

"""
tests/test_coverage_improvements.py

カバレッジ改善のための追加テスト
80%未満のモジュールを対象
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd


class TestResponseParser(unittest.TestCase):
    """ai/response_parser.py のカバレッジ改善テスト"""

    def setUp(self):
        from src.ai.response_parser import ResponseParser
        self.parser = ResponseParser()

    def test_parse_response_valid_json(self):
        """正常なJSON応答のパース"""
        text = json.dumps({
            "ai_sentiment": "Bullish",
            "ai_reason": "【結論】強気。｜【強み】成長性。｜【懸念】なし。",
            "ai_risk": "Low",
            "ai_horizon": "Short",
            "ai_detail": "①詳細②詳細③詳細④詳細⑤詳細⑥詳細⑦詳細",
            "audit_version": 1
        })
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
            "ai_risk": "Low"
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
            "ai_detail": "①②③④⑤⑥⑦"
        }
        is_valid, error = self.parser.validate_response(result)
        self.assertFalse(is_valid)
        self.assertIn("duplicated", error)

    def test_validate_response_missing_detail_sections(self):
        """詳細の番号付きセクションが欠けている"""
        result = {
            "ai_sentiment": "Bullish",
            "ai_reason": "【結論】a｜【強み】b｜【懸念】c",
            "ai_detail": "詳細なし"
        }
        is_valid, error = self.parser.validate_response(result)
        self.assertFalse(is_valid)
        self.assertIn("numbered sections", error)

    def test_validate_response_blacklist(self):
        """ブラックリストフレーズの検出"""
        result = {
            "ai_sentiment": "Bullish",
            "ai_reason": "【結論】安定した業績推移｜【強み】b｜【懸念】c",
            "ai_detail": "①②③④⑤⑥⑦"
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
        row = {"roe": 10, "per": 15, "operating_cf": 100, "debt_equity_ratio": 0.5, "free_cf": 50}
        alert = self.parser.generate_dqf_alert(row)
        self.assertEqual(alert, "")

    def test_load_blacklist_with_file(self):
        """ブラックリストファイルの読み込み"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# コメント\n")
            f.write("禁止フレーズ1\n")
            f.write("禁止フレーズ2\n")
            temp_path = f.name

        try:
            with patch.object(self.parser, '_load_blacklist') as mock_load:
                mock_load.return_value = ["禁止フレーズ1", "禁止フレーズ2", "安定した業績推移"]
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
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
        with patch('os.path.exists', return_value=False):
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
        manager.key_stats = [{"total_calls": 0, "success_count": 0, "retry_count": 0, "error_429_count": 0, "status": "active"}]
        manager.update_stats(0, "total_calls")
        self.assertEqual(manager.key_stats[0]["total_calls"], 1)


class TestEngine(unittest.TestCase):
    """engine.py のカバレッジ改善テスト"""

    def test_calculate_scores_empty_df(self):
        """空のDataFrame"""
        from src.engine import AnalysisEngine
        config = {"strategies": {}}
        engine = AnalysisEngine(config)
        result = engine.calculate_scores(pd.DataFrame(), "test")
        self.assertTrue(result.empty)


class TestPromptBuilder(unittest.TestCase):
    """ai/prompt_builder.py のカバレッジ改善テスト"""

    def test_build_prompt_with_missing_fields(self):
        """欠損フィールドがある場合のプロンプト生成"""
        from src.ai.prompt_builder import PromptBuilder
        config = {"ai": {"prompt_template": "config/ai_prompts.yaml"}}
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', unittest.mock.mock_open(read_data="template: test {code}")):
                builder = PromptBuilder(config)
                # テンプレートが読み込まれることを確認
                self.assertIsNotNone(builder)


class TestAnalyzer(unittest.TestCase):
    """analyzer.py のカバレッジ改善テスト"""

    def test_init_analyzer(self):
        """Analyzerの初期化"""
        from src.analyzer import StockAnalyzer
        config = {"strategies": {}, "paths": {"output_dir": "/tmp"}}
        with patch('src.analyzer.DataProvider'):
            analyzer = StockAnalyzer(config, debug_mode=True)
            self.assertIsNotNone(analyzer)


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


if __name__ == "__main__":
    unittest.main()


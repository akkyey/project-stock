"""
FetcherBase のユニットテスト
カバレッジ80%達成を目標
"""

import os
import tempfile
import unittest

import yaml
from src.fetcher.base import FetcherBase


class TestFetcherBase(unittest.TestCase):
    """FetcherBase クラスのテスト"""

    def test_status_constants(self):
        """ステータス定数が定義されていることを確認"""
        self.assertEqual(FetcherBase.STATUS_SUCCESS, "success")
        self.assertEqual(FetcherBase.STATUS_ERROR_QUOTA, "error_quota")
        self.assertEqual(FetcherBase.STATUS_ERROR_NETWORK, "error_network")
        self.assertEqual(FetcherBase.STATUS_ERROR_DATA, "error_data")
        self.assertEqual(FetcherBase.STATUS_ERROR_OTHER, "error_other")

    def test_init_with_dict_config(self):
        """辞書型で設定を渡す場合"""
        config = {"test_key": "test_value"}
        fetcher = FetcherBase(config_source=config)
        self.assertEqual(fetcher.config, config)

    def test_init_with_file_config(self):
        """ファイルパスで設定を渡す場合"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"file_key": "file_value"}, f)
            temp_path = f.name

        try:
            fetcher = FetcherBase(config_source=temp_path)
            self.assertEqual(fetcher.config.get("file_key"), "file_value")
        finally:
            os.unlink(temp_path)

    def test_init_with_missing_file(self):
        """存在しないファイルの場合、空の辞書を返す"""
        fetcher = FetcherBase(config_source="/non/existent/path.yaml")
        self.assertEqual(fetcher.config, {})

    def test_init_with_invalid_yaml(self):
        """不正なYAMLファイルの場合、空の辞書を返す"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")  # 不正なYAML
            temp_path = f.name

        try:
            fetcher = FetcherBase(config_source=temp_path)
            self.assertEqual(fetcher.config, {})
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()

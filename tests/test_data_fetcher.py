import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from src.fetcher import DataFetcher


class TestDataFetcher(unittest.TestCase):
    def setUp(self):
        # ネットワーク接続を避けるために空の設定を渡す
        self.fetcher = DataFetcher(
            config_source={
                "data": {
                    "jp_stock_list": "data/input/test_list.csv",
                    "output_path": "data/output/test_result.csv",
                },
                "ai": {"interval_sec": 0},
            }
        )

    @patch("src.fetcher.jpx.requests.Session")
    def test_fetch_jpx_list_normal(self, mock_session_cls):
        """JPXリスト取得の正常系テスト"""
        mock_session = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.content = b"dummy"
        mock_session.get.return_value = mock_response

        # pd.read_excel をモックしてデータを返すようにする
        with patch("src.fetcher.jpx.pd.read_excel") as mock_read:
            mock_read.return_value = pd.DataFrame(
                {
                    "コード": ["1301", "7203"],
                    "銘柄名": ["Kyokuyo", "Toyota"],
                    "33業種区分": ["Fishery", "Car"],
                    "市場・商品区分": ["Prime", "Prime"],
                }
            )
            df = self.fetcher.fetch_jpx_list(save_to_csv=False)
            self.assertEqual(len(df), 2)
            self.assertIn("code", df.columns)

    @patch("src.fetcher.jpx.requests.Session")
    @patch("src.fetcher.jpx.glob.glob")
    @patch("src.fetcher.jpx.pd.read_csv")
    @patch("src.fetcher.jpx.os.path.exists")
    def test_fetch_jpx_list_fallback(
        self, mock_exists, mock_read_csv, mock_glob, mock_session_cls
    ):
        """JPXリスト取得失敗時のフォールバックテスト"""
        mock_session = mock_session_cls.return_value
        mock_session.get.side_effect = Exception("Network Down")

        mock_exists.return_value = False
        mock_glob.return_value = ["data/input/stock_master_backup.csv"]
        # 必要なカラムをすべて含むDataFrameを返す
        mock_read_csv.return_value = pd.DataFrame(
            {
                "コード": ["9999"],
                "銘柄名": ["Backup"],
                "33業種区分": ["Others"],
                "市場・商品区分": ["Others"],
            }
        )

        df = self.fetcher.fetch_jpx_list(fallback_on_error=True)
        self.assertEqual(df.iloc[0]["code"], "9999")

    @patch("src.fetcher.yahoo.yf.Ticker")
    def test_fetch_single_stock_success(self, mock_ticker):
        """単一銘柄データ取得の成功テスト"""
        instance = mock_ticker.return_value
        instance.info = {
            "currentPrice": 1000,
            "trailingPE": 15.0,
            "priceToBook": 1.2,
            "dividendYield": 0.03,
            "regularMarketOpen": 950,
            "longName": "Test Corp",
        }
        # テクニカル指標計算用のヒストリカルデータ
        hist_df = pd.DataFrame(
            {
                "Open": [900] * 100,
                "High": [1100] * 100,
                "Low": [800] * 100,
                "Close": [1000] * 100,
                "Volume": [10000] * 100,
            },
            index=pd.date_range("2023-01-01", periods=100),
        )
        instance.history.return_value = hist_df

        data = self.fetcher._fetch_single_stock("1301")
        self.assertEqual(data["code"], "1301")
        self.assertEqual(data["price"], 1000)
        self.assertIn("rsi_14", data)
        self.assertIn("macd_hist", data)

    @patch("src.fetcher.yahoo.yf.Ticker")
    def test_fetch_single_stock_error(self, mock_ticker):
        """データ取得失敗時の挙動"""
        instance = mock_ticker.return_value
        instance.info = {}  # infoが空
        instance.history.side_effect = Exception("API Error")

        data = self.fetcher._fetch_single_stock("0000")
        data = self.fetcher._fetch_single_stock("0000")
        self.assertIsNotNone(data)
        self.assertEqual(data.get("fetch_status"), "error_data")
        self.assertEqual(data.get("code"), "0000")


if __name__ == "__main__":
    unittest.main()

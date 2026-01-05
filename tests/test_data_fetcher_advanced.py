import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
import requests

from src.fetcher import DataFetcher
from src.fetcher.technical import calc_technical_indicators


class TestDataFetcherAdvanced(unittest.TestCase):
    def setUp(self):
        self.config = {
            "data": {
                "jp_stock_list": "data/test_stock_list.csv",
                "output_path": "data/test_output.csv",
            }
        }
        self.fetcher = DataFetcher(self.config)

    @patch("src.fetcher.jpx.requests.Session")
    def test_fetch_jpx_list_download_success(self, MockSession):
        """Test successful download logic"""
        # Mock session on the JPX fetcher instance
        mock_session = MockSession.return_value
        mock_resp = MagicMock()
        mock_resp.content = b""
        mock_session.get.return_value = mock_resp

        # We also need to patch pd.read_excel used in jpx.py
        with patch("src.fetcher.jpx.pd.read_excel") as mock_read_excel:
            mock_read_excel.return_value = pd.DataFrame(
                [
                    {
                        "コード": "1001",
                        "銘柄名": "A",
                        "33業種区分": "Tech",
                        "市場・商品区分": "Prime",
                    }
                ]
            )

            df = self.fetcher.fetch_jpx_list(save_to_csv=False)
            self.assertEqual(len(df), 1)
            self.assertEqual(df.iloc[0]["code"], "1001")

    @patch("src.fetcher.jpx.requests.Session")
    def test_fetch_jpx_list_download_fail_no_fallback(self, MockSession):
        """Test download failure raises exception"""
        mock_session = MockSession.return_value
        mock_session.get.side_effect = Exception("Network Down")

        with self.assertRaises(Exception):
            self.fetcher.fetch_jpx_list(fallback_on_error=False, save_to_csv=False)

    @patch("src.fetcher.jpx.glob.glob")
    @patch("src.fetcher.jpx.requests.Session")
    def test_fetch_jpx_list_fallback_success(self, MockSession, mock_glob):
        """Test fallback to backup file"""
        mock_session = MockSession.return_value
        mock_session.get.side_effect = Exception("Network Down")

        # Backup found
        mock_glob.return_value = ["data/stock_master_20240101.csv"]

        with patch("src.fetcher.jpx.pd.read_csv") as mock_read_csv:
            mock_read_csv.return_value = pd.DataFrame(
                [
                    {
                        "code": "2001.0",
                        "name": "B",
                        "sector": "Auto",
                        "market": "Standard",
                    }
                ]
            )

            df = self.fetcher.fetch_jpx_list(fallback_on_error=True, save_to_csv=False)
            self.assertEqual(len(df), 1)
            self.assertEqual(df.iloc[0]["code"], "2001")  # Should clean .0

    def test_calc_technical_indicators_empty(self):
        """Test technical calc short history"""
        hist = pd.DataFrame()
        res = calc_technical_indicators(hist)
        self.assertEqual(res, {})

    @patch("src.fetcher.yahoo.yf.Ticker")
    def test_fetch_single_stock_quota_error(self, MockTicker):
        """Test 429 Error handling"""
        # Patch the METHOD on the yahoo_fetcher INSTANCE
        with patch.object(
            self.fetcher.yahoo_fetcher,
            "_get_ticker_info_safe",
            side_effect=Exception("429 Too Many Requests"),
        ):
            res = self.fetcher._fetch_single_stock("9999")
            self.assertEqual(res["fetch_status"], DataFetcher.STATUS_ERROR_QUOTA)

    @patch("src.fetcher.yahoo.yf.Ticker")
    def test_fetch_single_stock_network_error(self, MockTicker):
        """Test Connection Error handling"""
        with patch.object(
            self.fetcher.yahoo_fetcher,
            "_get_ticker_info_safe",
            side_effect=requests.exceptions.ConnectionError,
        ):
            res = self.fetcher._fetch_single_stock("9999")
            self.assertEqual(res["fetch_status"], DataFetcher.STATUS_ERROR_NETWORK)

    @patch("src.fetcher.yahoo.yf.Ticker")
    def test_fetch_single_stock_turnaround(self, MockTicker):
        """Test Turnaround logic"""
        mock_info = {"currentPrice": 100}
        with patch.object(
            self.fetcher.yahoo_fetcher, "_get_ticker_info_safe", return_value=mock_info
        ):
            mock_stock = MockTicker.return_value
            # Income stmt
            inc_df = pd.DataFrame(
                {"2024": [1000], "2023": [-500]}, index=["Net Income"]
            )
            mock_stock.financials = inc_df
            # Also mock balance_sheet and cashflow to avoid empty dataframe warnings or logic issues if called
            mock_stock.balance_sheet = pd.DataFrame()
            mock_stock.cashflow = pd.DataFrame()
            mock_stock.history.return_value = pd.DataFrame()

            res = self.fetcher._fetch_single_stock("7777", deep_repair=True)
            self.assertEqual(res["is_turnaround"], 1)

    @patch("src.fetcher.yahoo.yf.Ticker")
    @patch("time.sleep")  # Speedup
    def test_fetch_stock_data_orchestration(self, mock_sleep, MockTicker):
        """Test batch fetch loop logic"""
        mock_info = {"currentPrice": 100, "longName": "Orch Test"}
        with patch.object(
            self.fetcher.yahoo_fetcher, "_get_ticker_info_safe", return_value=mock_info
        ):
            MockTicker.return_value.history.return_value = pd.DataFrame()

            # Case 1: Provided codes
            codes = ["1001", "1002"]
            df = self.fetcher.fetch_stock_data(codes)
            self.assertEqual(len(df), 2)
            self.assertEqual(df.iloc[0]["code"], "1001")

            # Case 2: Empty codes (should fetch list)
            # Mock fetch_jpx_list via delegation
            with patch.object(self.fetcher.jpx_fetcher, "fetch_jpx_list") as mock_jpx:
                mock_jpx.return_value = pd.DataFrame([{"code": "9999"}])
                df2 = self.fetcher.fetch_stock_data(None)
                self.assertEqual(len(df2), 1)
                self.assertEqual(df2.iloc[0]["code"], "9999")


if __name__ == "__main__":
    unittest.main()

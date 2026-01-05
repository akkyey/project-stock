import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from src.fetcher.yahoo import YahooFetcher


class TestYahooFetcherCoverage(unittest.TestCase):
    def setUp(self):
        self.config = {}
        self.fetcher = YahooFetcher(self.config)

    @patch("src.fetcher.yahoo.time.sleep")
    def test_get_ticker_info_safe_retry(self, mock_sleep):
        """Test retry logic and 401 handling"""
        mock_ticker = MagicMock()
        # Side effect: 1st call raises 401, 2nd call raises other error, 3rd succeeds
        mock_ticker.info = {}
        # But `ticker.info` is a property effectively (or attribute accessed).
        # We need to mock the property modification or use property mock?
        # The code accesses `ticker.info`. If we want it to raise, we need PropertyMock or similar,
        # or just mock the instance to raise on access if possible, but easier to wrap.
        # However, _get_ticker_info_safe takes `ticker` object.

        # Let's mock the ticker object such that accessing .info raises side_effect
        type(mock_ticker).info = unittest.mock.PropertyMock(
            side_effect=[
                Exception("401 Unauthorized"),
                Exception("Network Error"),
                {"currentPrice": 100},
            ]
        )

        res = self.fetcher._get_ticker_info_safe(mock_ticker)
        self.assertEqual(res["currentPrice"], 100)
        # Should have slept for panic (10s) + retry delay
        self.assertTrue(mock_sleep.called)

    @patch("src.fetcher.yahoo.yf.Ticker")
    @patch("src.fetcher.yahoo.time.sleep")
    def test_fetch_single_stock_equity_ratio_logic(self, mock_sleep, MockTicker):
        """Test Tiered Equity Ratio Logic"""
        # Case 1: Info has equityRatio
        mock_stock = MockTicker.return_value
        mock_stock.info = {"currentPrice": 100, "equityRatio": 40.0}

        with patch.object(
            self.fetcher, "_get_ticker_info_safe", return_value=mock_stock.info
        ):
            res = self.fetcher.fetch_single_stock("1001")
            self.assertEqual(res["equity_ratio"], 40.0)

        # Case 2: Estimate via D/E
        mock_stock.info = {
            "currentPrice": 100,
            "equityRatio": None,
            "debtToEquity": 100,
        }
        with patch.object(
            self.fetcher, "_get_ticker_info_safe", return_value=mock_stock.info
        ):
            res = self.fetcher.fetch_single_stock("1002")
            # D/E = 100 -> Debt=Eq -> EqRatio = 50%
            self.assertAlmostEqual(res["equity_ratio"], 50.0)

        # Case 3: Estimate via BV/Debt
        # BV=100, Shares=10 -> Equity=1000. Debt=1000. Total=2000. Ratio=50%
        mock_stock.info = {
            "currentPrice": 100,
            "equityRatio": None,
            "debtToEquity": None,
            "bookValue": 100,
            "sharesOutstanding": 10,
            "totalDebt": 1000,
        }
        with patch.object(
            self.fetcher, "_get_ticker_info_safe", return_value=mock_stock.info
        ):
            res = self.fetcher.fetch_single_stock("1003")
            self.assertAlmostEqual(res["equity_ratio"], 50.0)

    @patch("src.fetcher.yahoo.yf.Ticker")
    @patch("src.fetcher.yahoo.time.sleep")
    def test_fetch_single_stock_deep_repair(self, mock_sleep, MockTicker):
        """Test Deep Repair logic for Equity/PER/CF"""
        mock_stock = MockTicker.return_value
        # Info missing criticals
        mock_stock.info = {
            "currentPrice": 1000,
            "equityRatio": None,
            "trailingPE": None,
            "operatingCashflow": None,
        }

        # Setup Financials for Deep Repair
        # BS: Assets=2000, Equity=1000 -> Ratio 50%
        mock_stock.balance_sheet = pd.DataFrame(
            {"2024-03-31": [2000, 1000]},
            index=["Total Assets", "Total Stockholder Equity"],
        )

        # CF: OCF = 500
        mock_stock.cashflow = pd.DataFrame(
            {"2024-03-31": [500]}, index=["Operating Cash Flow"]
        )

        # Inc: Net Income = 100. Shares=10 (from BS 'Share Issued' mock needed?)
        # Logic uses BS for shares or info?
        # Code: `shares = get_latest_value(bs, ['Ordinary Shares Number', 'Share Issued'])`
        mock_stock.financials = pd.DataFrame(
            {"2024-03-31": [100]}, index=["Net Income"]
        )

        # Add shares to BS
        mock_stock.balance_sheet.loc["Ordinary Shares Number"] = [10]

        with patch.object(
            self.fetcher, "_get_ticker_info_safe", return_value=mock_stock.info
        ):
            # Run with deep_repair=True
            res = self.fetcher.fetch_single_stock("1004", deep_repair=True)

            self.assertEqual(res["equity_ratio"], 50.0)  # 1000/2000
            self.assertEqual(res["operating_cf"], 500)
            # PER: EPS = 100 / 10 = 10. Price=1000. PER = 100.
            self.assertEqual(res["per"], 100.0)

    @patch("src.fetcher.yahoo.yf.Ticker")
    @patch("src.fetcher.yahoo.time.sleep")
    def test_turnaround_status_logic(self, mock_sleep, MockTicker):
        """Test Profit Status / Turnaround Logic branches"""
        mock_stock = MockTicker.return_value
        mock_stock.info = {"currentPrice": 100}

        # Helper to set financials and check status
        def check_status(prev, curr, expected_turn, expected_profit, growth_chk=None):
            mock_stock.financials = pd.DataFrame(
                {"Curr": [curr], "Prev": [prev]}, index=["Net Income"]
            )

            with patch.object(
                self.fetcher, "_get_ticker_info_safe", return_value=mock_stock.info
            ):
                res = self.fetcher.fetch_single_stock("9000")
                self.assertEqual(res["turnaround_status"], expected_turn)
                self.assertEqual(res["profit_status"], expected_profit)
                if growth_chk:
                    self.assertAlmostEqual(res["profit_growth"], growth_chk)

        # 1. Turnaround Black (Neg -> Pos)
        check_status(-100, 100, "turnaround_black", "turnaround")

        # 2. Turnaround White (Pos -> Neg) -> Crash
        check_status(100, -100, "turnaround_white", "crash")

        # 3. Loss Shrinking (Neg -> Less Neg)
        check_status(-100, -50, "loss_shrinking", "loss_shrinking")

        # 4. Loss Expanding (Neg -> More Neg)
        check_status(-50, -100, "loss_expanding", "loss_expanding")

        # 5. Profit Surge (>100% growth) (10 -> 30) = +200%
        check_status(10, 30, "profit_surge", "surge", 200.0)

        # 6. High Growth (30% <= g < 100%) (10 -> 15) = +50%
        check_status(
            10, 15, "normal", "high_growth", 50.0
        )  # status default is normal if not surge/crash?
        # Code: elif 30 <= g < 100: profit_status='high_growth'. turnaround_status not set (remains 'normal' init)

        # 7. Stable (-30 <= g < 30) (10 -> 11) = +10%
        check_status(10, 11, "normal", "stable", 10.0)

        # 8. Profit Crash (g < -30) (10 -> 5) = -50%
        check_status(10, 5, "profit_crash", "crash", -50.0)

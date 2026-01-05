from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from src.sentinel import Sentinel


class TestSentinelUnit:
    @pytest.fixture
    def sentinel(self):
        # Mock dependencies in __init__
        with (
            patch("src.sentinel.ConfigLoader"),
            patch("src.sentinel.StockDatabase"),
            patch("src.sentinel.DataFetcher"),
            patch("src.sentinel.AnalysisEngine"),
        ):
            s = Sentinel(debug_mode=True)
            # Mock internal logger
            s.logger = MagicMock()
            return s

    def test_process_yf_df_valid(self, sentinel):
        # Create a sample DataFrame that simulates 30 days of data
        dates = pd.date_range(end="2025-01-01", periods=30)
        close = np.linspace(100, 110, 30)  # Uptrend
        df = pd.DataFrame({"Close": close}, index=dates)

        # Add volatility at the end
        df.iloc[-1, df.columns.get_loc("Close")] = (
            120  # Jump from 110 (approx) to 120 ~ 9%
        )

        res = sentinel._process_yf_df(df, "9999")
        assert res is not None
        assert res["code"] == "9999"
        assert res["price"] == 120
        assert res["change_pct"] > 5.0
        assert "macd" in res
        assert "golden_cross" in res

    def test_process_yf_df_empty(self, sentinel):
        assert sentinel._process_yf_df(pd.DataFrame(), "9999") is None
        assert sentinel._process_yf_df(pd.DataFrame({"Close": [1]}), "9999") is None

    def test_detect_volatility(self, sentinel):
        sentinel._save_alert = MagicMock()

        data_map = {
            "1111": {"price": 100, "change_pct": 1.0},  # No alert
            "2222": {"price": 200, "change_pct": 6.0},  # Skyrocket
            "3333": {"price": 300, "change_pct": -5.5},  # Plunge
        }

        sentinel._detect_volatility(data_map)

        assert sentinel._save_alert.call_count == 2
        calls = sentinel._save_alert.call_args_list
        codes = [c[0][0] for c in calls]
        assert "2222" in codes
        assert "3333" in codes
        assert "1111" not in codes

    def test_detect_technical_signals(self, sentinel):
        sentinel._save_alert = MagicMock()

        data_map = {"A": {"golden_cross": False}, "B": {"golden_cross": True}}

        sentinel._detect_technical_signals(data_map)

        sentinel._save_alert.assert_called_once()
        args = sentinel._save_alert.call_args[0]
        assert args[0] == "B"
        assert args[1] == "technical"

    def test_detect_rank_fluctuations_entry(self, sentinel):
        # Mock sentinel.config
        sentinel.config = {"strategies": {"TestStrat": {}}}
        sentinel._save_alert = MagicMock()

        # 1. Mock RankHistory (Official Top 5) -> Only code 'Old1'...'Old5'
        mock_rank_query = MagicMock()
        # Return dicts: [{'code': 'Old1', 'rank': 1}...]
        mock_rank_query.dicts.return_value = [
            {"code": f"Old{i}", "rank": i} for i in range(1, 6)
        ]

        # Patch models.RankHistory.select chain
        with patch("src.sentinel.RankHistory") as MockRH:
            # Chain: select...where...order_by...limit...dicts
            MockRH.select.return_value.where.return_value.order_by.return_value.limit.return_value = (
                mock_rank_query
            )

            # 2. Mock Fetcher (Base DF)
            # Should include 'NewEntrant'
            base_df = pd.DataFrame(
                [
                    {"code": "Old1", "current_price": 100},
                    {"code": "NewEntrant", "current_price": 50},
                ]
            )
            sentinel.fetcher.fetch_data_from_db.return_value = base_df

            # 3. Mock Engine (Scored)
            # NewEntrant gets Rank 1!
            scored_df = pd.DataFrame(
                [
                    {"code": "NewEntrant", "quant_score": 100},
                    {"code": "Old1", "quant_score": 90},
                    # Others low... logic needs top 5.
                    # If we only return 2 rows, head(5) is these 2.
                    # So NewEntrant is Rank 1, Old1 is Rank 2.
                ]
            )
            sentinel.engine.calculate_scores.return_value = scored_df

            # Data map for loop trigger
            data_map = {"Old1": {"price": 100}, "NewEntrant": {"price": 50}}

            sentinel._detect_rank_fluctuations(data_map)

            # Verify Alert for NewEntrant (Entered Top 5)
            # Old1 is still in Top 5 (Rank 2), so no Fall alert (it was Rank 1, now 2, but stayed in top 5 list).

            # Check save_alert calls
            # Expected: NewEntrant (Entry)
            # Did any Old fall out?
            # Official: Old1..Old5.
            # New: NewEntrant, Old1.
            # Old2..Old5 are MISSING from New List (since scored_df only had 2 items).
            # So logic should flag Old2..Old5 as FALLEN.

            calls = sentinel._save_alert.call_args_list
            codes = [c[0][0] for c in calls]
            msg_types = [c[0][1] for c in calls]

            assert "NewEntrant" in codes
            assert "rank_change" in msg_types

            # Also check if Old2 fell
            assert "Old2" in codes

    def test_run_flow(self, sentinel):
        # Test the main run loop orchestration
        sentinel._get_surveillance_targets = MagicMock(return_value=["1001"])
        sentinel._scan_market = MagicMock(return_value={"1001": {"change_pct": 0}})
        sentinel._detect_volatility = MagicMock()
        sentinel._detect_technical_signals = MagicMock()
        sentinel._detect_rank_fluctuations = MagicMock()

        sentinel.run()

        sentinel._scan_market.assert_called_with(["1001"])
        sentinel._detect_volatility.assert_called()

    def test_get_surveillance_targets(self, sentinel):
        # Test the query logic (Mocking DB models)
        # We need to mock the chain: MarketData.select().join().distinct()

        # Create a mock query result
        mock_row1 = MagicMock()
        mock_row1.code_id = "1001"
        mock_row2 = MagicMock()
        mock_row2.code_id = "1002"

        # Patch the MarketData used in sentinel
        with (
            patch("src.sentinel.MarketData") as MockMD,
            patch("src.sentinel.AnalysisResult"),
        ):

            # Setup the chain
            mock_query_obj = [mock_row1, mock_row2]
            MockMD.select.return_value.join.return_value.distinct.return_value = (
                mock_query_obj
            )

            targets = sentinel._get_surveillance_targets(limit=10)

            assert len(targets) == 2
            assert "1001" in targets
            assert "1002" in targets
            MockMD.select.assert_called()

    def test_scan_market_batch(self, sentinel):
        # Test _scan_market logic including batching and yf.download
        codes = ["1001", "1002"]

        # Mock yfinance.download
        # Since 'import yfinance as yf' is inside the method, we must patch 'yfinance.download' globally?
        # Or mock the module lookup
        with patch("yfinance.download") as mock_download:
            # Setup return DF
            # Multi-level columns if group_by='ticker'
            # Tickers: 1001.T, 1002.T
            # Columns: (1001.T, 'Close') ...

            # Simple approach: Return a DF that behaves like result
            # But Sentinel iterates `df[ticker]`.

            # Mock Data
            dates = pd.date_range("2025-01-01", periods=5)
            # Create MultiIndex DF
            iterables = [
                ["1001.T", "1002.T"],
                ["Close", "Open", "High", "Low", "Volume"],
            ]
            cols = pd.MultiIndex.from_product(iterables, names=["Ticker", "Price"])
            df = pd.DataFrame(np.random.randn(5, 10), index=dates, columns=cols)
            # Ensure safe values
            df.loc[:, (slice(None), "Close")] = 100.0

            mock_download.return_value = df

            # We also need to mock _process_yf_df to verify it's called
            # (or let it run if it's simple enough, but we want to isolate _scan_market flow)
            # Let's let it run (integration style unit test) OR mock it.
            # Mocking it allows verifying calls.
            sentinel._process_yf_df = MagicMock(return_value={"code": "OK"})

            results = sentinel._scan_market(codes)

            assert len(results) == 2
            assert "1001" in results
            assert "1002" in results

            # Check download call
            mock_download.assert_called()
            # Verify batch ticker format
            args = mock_download.call_args
            assert "1001.T" in args[0][0]

    def test_scan_market_single(self, sentinel):
        # Test single code path
        codes = ["9999"]
        with patch("yfinance.download") as mock_download:
            # Single ticker download returns regular Index (not Multi) usually,
            # BUT group_by='ticker' forces struct?
            # Sentinel logic checks len(batch) == 1

            dates = pd.date_range("2025-01-01", periods=5)
            df = pd.DataFrame({"Close": [100] * 5}, index=dates)
            mock_download.return_value = df

            sentinel._process_yf_df = MagicMock(return_value={"code": "9999"})

            results = sentinel._scan_market(codes)

            assert "9999" in results
            sentinel._process_yf_df.assert_called_with(df, "9999")

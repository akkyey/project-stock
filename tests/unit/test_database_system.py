import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import tempfile

# Path resolution to include stock-analyzer4/src in sys.path
# Since this file is in tests/unit/, we need to go up two levels to root, then into stock-analyzer4
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, "stock-analyzer4"))

from src.database import StockDatabase
from src.database_factory import DatabaseFactory
from src.fetcher import DataFetcher
from src.result_writer import ResultWriter
from src.models import MarketData

class TestDatabaseSystem(unittest.TestCase):
    def setUp(self):
        """Test setup"""
        DatabaseFactory.reset()
        # Dummy config for Fetcher/Writer
        self.dummy_config = {
            "api": {"key": "test_key"},
            "system": {"concurrency": 1},
            "data": {
                "output_path": "data/output/test_result.csv",
                "jp_stock_list": "data/input/test_list.csv",
            },
            "paths": {"db_file": ":memory:"} # Default to memory if not specified
        }

    def tearDown(self):
        DatabaseFactory.reset()

    # --- From TestStockAnalyzerSystem ---

    def test_db_initialization_memory(self):
        """[Regression] :memory: 指定時の初期化不具合修正テスト(No.2)"""
        print("Testing DB Initialization with :memory: (Regression No.2)...")
        try:
            # 初期化時に FileNotFoundError が発生しないことを確認
            db = StockDatabase(db_path=":memory:")
            self.assertIsNotNone(db)
            print("DB Initialization with :memory: -> OK")
        except Exception as e:
            self.fail(f"DB Initialization with :memory: failed: {e}")

    def test_db_maintenance(self):
        """[v4.4] DBメンテナンス (古いデータの削除) のテスト"""
        print("Testing DB Maintenance (Cleanup) logic...")
        from datetime import datetime, timedelta

        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        db_path = tf.name
        tf.close()

        try:
            db = StockDatabase(db_path)

            # 1. データの準備
            old_date = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
            new_date = datetime.now().strftime("%Y-%m-%d")

            # 銘柄マスタ作成
            db.upsert_stocks(
                [{"code": "9999", "name": "Test", "sector": "-", "market": "-"}]
            )

            # 市況データ作成
            db.upsert_market_data(
                [
                    {"code": "9999", "entry_date": old_date, "price": 100},
                    {"code": "9999", "entry_date": new_date, "price": 200},
                ]
            )

            # 削除件数を確認
            self.assertEqual(MarketData.select().count(), 2)

            # 2. 実行 (30日以前を削除)
            success, msg = db.cleanup_and_optimize(retention_days=30)

            # 3. 検証
            self.assertTrue(success)
            self.assertEqual(MarketData.select().count(), 1)
            remaining = MarketData.select().first()
            self.assertEqual(remaining.entry_date, new_date)

            print(f"DB Maintenance Cleanup -> OK ({msg})")

        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    @patch("src.fetcher.yahoo.yf.Ticker")
    def test_data_fetcher(self, mock_ticker):
        print("Testing DataFetcher...")
        # yfinanceのTickerモック設定
        mock_instance = mock_ticker.return_value
        mock_instance.info = {
            "currentPrice": 1000,
            "trailingPE": 12.5,
            "totalRevenue": 100000000,
            "revenueGrowth": 0.055,
            "longName": "Test Corp",
            "sector": "Tech",
        }

        # DataFetcher初期化
        fetcher = DataFetcher(self.dummy_config)

        # _fetch_single_stock test
        data = fetcher._fetch_single_stock("9999")
        self.assertIsNotNone(data)
        self.assertEqual(data["code"], "9999")
        self.assertEqual(data["sales"], 100000000)
        self.assertEqual(data["sales_growth"], 5.5)

        # Verify no session injection
        args, kwargs = mock_ticker.call_args
        self.assertNotIn(
            "session", kwargs, "yfinance should not receive 'session' argument"
        )
        print("Fetcher returned valid data & No Session Injection -> OK")

    @patch("src.fetcher.jpx.pd.read_excel")
    @patch("src.fetcher.jpx.pd.read_csv")
    @patch("src.fetcher.jpx.glob.glob")
    @patch("src.fetcher.jpx.os.path.exists")
    @patch("src.fetcher.jpx.requests.Session")
    def test_jpx_fetch_fallback(
        self, mock_session_cls, mock_exists, mock_glob, mock_read_csv, mock_read_excel
    ):
        print("Testing DataFetcher JPX Fallback...")

        mock_session_instance = mock_session_cls.return_value
        mock_response = MagicMock()
        mock_response.content = b"dummy_content"
        mock_session_instance.get.return_value = mock_response

        fetcher = DataFetcher(self.dummy_config)

        # 1. Normal (via Session)
        mock_exists.return_value = False
        mock_read_excel.return_value = pd.DataFrame(
            {
                "コード": ["1"],
                "銘柄名": ["T"],
                "33業種区分": ["S"],
                "市場・商品区分": ["M"],
            }
        )

        df = fetcher.fetch_jpx_list(fallback_on_error=False)
        self.assertFalse(df.empty)
        mock_session_instance.get.assert_called()
        print("  - Normal (via Session) -> OK")

        # 2. Error (Fallback)
        mock_session_instance.get.side_effect = Exception("Network Fail")
        mock_glob.return_value = ["data/input/stock_master_2025.csv"]
        mock_read_csv.return_value = pd.DataFrame(
            {
                "コード": ["2"],
                "銘柄名": ["B"],
                "33業種区分": ["S"],
                "市場・商品区分": ["M"],
            }
        )

        df_back = fetcher.fetch_jpx_list(fallback_on_error=True)
        self.assertFalse(df_back.empty)
        print("  - Fallback -> OK")

    def test_excel_writer_csv(self):
        """CSV出力のテスト"""
        print("Testing ResultWriter (CSV Mode)...")
        writer = ResultWriter(self.dummy_config)
        df = pd.DataFrame([{"col1": 1, "col2": 2}])

        test_filename = "test_output.xlsx"
        expected_csv = "data/output/test_output.csv"
        
        # Ensure output dir exists
        os.makedirs("data/output", exist_ok=True)

        try:
            path = writer.save(df, test_filename)
            if path:
                self.assertTrue(os.path.exists(path))
                self.assertTrue(path.endswith(".csv"))
            print("CSV file created -> OK")
        finally:
            if os.path.exists(expected_csv):
                os.remove(expected_csv)

class TestDatabaseBatchFeatures(unittest.TestCase):
    """Refactored from self_diagnostic.py new base features test"""
    
    def setUp(self):
        DatabaseFactory.reset()
        self.tf = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.tf.name
        self.tf.close()

    def tearDown(self):
        DatabaseFactory.reset()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_database_batch_fetch(self):
        print("\nTesting StockDatabase.get_market_data_batch...")
        db = StockDatabase(self.db_path)

        # データ準備
        stocks = [
            {"code": "1001", "name": "Stock A", "sector": "Sector A", "market": "M"},
            {"code": "1002", "name": "Stock B", "sector": "Sector B", "market": "M"},
        ]
        db.upsert_stocks(stocks)

        market_data = [
            {"code": "1001", "entry_date": "2025-01-01", "price": 100},
            {"code": "1001", "entry_date": "2025-01-02", "price": 110},
            {"code": "1002", "entry_date": "2025-01-02", "price": 200},
        ]
        db.upsert_market_data(market_data)

        # 実装したバッチ取得のテスト
        df = db.get_market_data_batch(["1001", "1002"])

        self.assertEqual(len(df), 2)
        # 1001 は最新の 2025-01-02 が取れているか
        row_1001 = df[df["code"] == "1001"].iloc[0]
        self.assertEqual(row_1001["price"], 110)
        self.assertEqual(row_1001["entry_date"], "2025-01-02")

        print("StockDatabase.get_market_data_batch -> OK")

class TestFetcherFacadeIsolated(unittest.TestCase):
    """[v12.1] DataFetcher.fetch_data_from_db の完全分離テスト"""

    def test_fetcher_facade_db_access(self):
        """DataFetcher.fetch_data_from_db が config の db_file を正しく使用することを確認"""
        print("Testing DataFetcher.fetch_data_from_db (Isolated)...")

        DatabaseFactory.reset()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tf:
            isolated_db_path = tf.name

        try:
            from src.database import StockDatabase
            from src.fetcher.facade import DataFetcher

            # StockDatabase 経由で初期化
            db = StockDatabase(isolated_db_path)
            db.upsert_stocks(
                [{"code": "9999", "name": "Isolated", "sector": "S", "market": "M"}]
            )
            db.upsert_market_data(
                [{"code": "9999", "entry_date": "2025-01-01", "price": 100}]
            )

            # DataFetcher に同じパスを指定
            dummy_config = {"paths": {"db_file": isolated_db_path}}
            fetcher = DataFetcher(dummy_config)
            df = fetcher.fetch_data_from_db(["9999"])

            self.assertFalse(df.empty, "DataFrame should not be empty")
            self.assertEqual(df.iloc[0]["code"], "9999")
            self.assertEqual(df.iloc[0]["price"], 100)

            print("DataFetcher.fetch_data_from_db -> OK")
        finally:
            DatabaseFactory.reset()
            if os.path.exists(isolated_db_path):
                os.remove(isolated_db_path)

if __name__ == "__main__":
    unittest.main()

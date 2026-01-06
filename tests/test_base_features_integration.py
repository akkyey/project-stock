# -*- coding: utf-8 -*-
"""
Base Features 統合テスト
`get_market_data_batch` および `fetch_data_from_db` のエンドツーエンドシナリオテスト。

テスト対象:
- src/database.py: StockDatabase.get_market_data_batch
- src/fetcher/facade.py: DataFetcher.fetch_data_from_db
"""
import os
import tempfile
import unittest
from datetime import datetime, timedelta

import pytest
from src.database import StockDatabase
from src.fetcher.facade import DataFetcher


@pytest.mark.integration
class TestBaseFeatures_GetMarketDataBatch(unittest.TestCase):
    """get_market_data_batch のエンドツーエンド統合テスト"""

    @classmethod
    def setUpClass(cls):
        """テストスイート全体で使用する一時DBを作成"""
        cls.tf = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        cls.db_path = cls.tf.name
        cls.tf.close()

        # db_proxyをリセット
        from src.database_factory import DatabaseFactory

        DatabaseFactory.reset()

        cls.db = StockDatabase(cls.db_path)

        # テストデータの準備
        stocks = [
            {
                "code": "1001",
                "name": "Stock A",
                "sector": "Technology",
                "market": "Prime",
            },
            {
                "code": "1002",
                "name": "Stock B",
                "sector": "Finance",
                "market": "Standard",
            },
            {"code": "1003", "name": "Stock C", "sector": "Retail", "market": "Growth"},
            {
                "code": "1004",
                "name": "Stock D",
                "sector": "Healthcare",
                "market": "Prime",
            },
            {
                "code": "1005",
                "name": "Stock E",
                "sector": "Energy",
                "market": "Standard",
            },
        ]
        cls.db.upsert_stocks(stocks)

        # 複数日にわたるマーケットデータ
        base_date = datetime(2025, 1, 1)
        market_data = []
        for i, code in enumerate(["1001", "1002", "1003", "1004", "1005"]):
            for day_offset in range(5):  # 5日分のデータ
                entry_date = (base_date + timedelta(days=day_offset)).strftime(
                    "%Y-%m-%d"
                )
                market_data.append(
                    {
                        "code": code,
                        "entry_date": entry_date,
                        "price": 1000
                        + (i * 100)
                        + (day_offset * 10),  # 価格に変動を持たせる
                        "volume": 100000 + (day_offset * 10000),
                        "per": 15.0 + i,
                        "pbr": 1.0 + (i * 0.1),
                        "roe": 10.0 + i,
                        "dividend_yield": 2.0 + (i * 0.5),
                        "equity_ratio": 50.0 + i,
                        "operating_cf": 1000000 * (i + 1),
                        "operating_margin": 10.0 + i,
                    }
                )
        cls.db.upsert_market_data(market_data)

    @classmethod
    def tearDownClass(cls):
        """テスト終了後のクリーンアップ"""
        from src.database_factory import DatabaseFactory

        DatabaseFactory.reset()
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_batch_fetch_single_code(self):
        """単一銘柄のバッチ取得"""
        df = self.db.get_market_data_batch(["1001"])

        self.assertFalse(df.empty)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["code"], "1001")
        # 最新日（2025-01-05）のデータが取得されること
        self.assertEqual(df.iloc[0]["entry_date"], "2025-01-05")
        self.assertEqual(df.iloc[0]["price"], 1040)  # 1000 + 0*100 + 4*10

    def test_batch_fetch_multiple_codes(self):
        """複数銘柄のバッチ取得"""
        df = self.db.get_market_data_batch(["1001", "1002", "1003"])

        self.assertFalse(df.empty)
        self.assertEqual(len(df), 3)

        # 各銘柄の最新データが取得されていること
        codes = df["code"].tolist()
        self.assertIn("1001", codes)
        self.assertIn("1002", codes)
        self.assertIn("1003", codes)

        # 全て最新日であること
        for _, row in df.iterrows():
            self.assertEqual(row["entry_date"], "2025-01-05")

    def test_batch_fetch_all_codes(self):
        """全銘柄のバッチ取得"""
        df = self.db.get_market_data_batch(["1001", "1002", "1003", "1004", "1005"])

        self.assertEqual(len(df), 5)

    def test_batch_fetch_nonexistent_code(self):
        """存在しない銘柄コードの処理"""
        df = self.db.get_market_data_batch(["9999"])

        self.assertTrue(df.empty)

    def test_batch_fetch_mixed_codes(self):
        """存在する銘柄と存在しない銘柄の混在"""
        df = self.db.get_market_data_batch(["1001", "9999", "1002"])

        self.assertEqual(len(df), 2)
        codes = df["code"].tolist()
        self.assertIn("1001", codes)
        self.assertIn("1002", codes)
        self.assertNotIn("9999", codes)

    def test_batch_fetch_financial_columns(self):
        """財務データカラムの取得確認"""
        df = self.db.get_market_data_batch(["1001"])

        # 重要な財務カラムが存在すること
        required_cols = [
            "per",
            "pbr",
            "roe",
            "dividend_yield",
            "equity_ratio",
            "operating_cf",
            "operating_margin",
        ]
        for col in required_cols:
            self.assertIn(col, df.columns, f"Missing column: {col}")

        # 値が正しいこと
        row = df.iloc[0]
        self.assertEqual(row["per"], 15.0)
        self.assertEqual(row["pbr"], 1.0)
        self.assertEqual(row["roe"], 10.0)


@pytest.mark.integration
class TestBaseFeatures_FetchDataFromDB(unittest.TestCase):
    """fetch_data_from_db のエンドツーエンド統合テスト（DataFetcher経由）"""

    @classmethod
    def setUpClass(cls):
        """テストスイート全体で使用する一時DBを作成"""
        cls.tf = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        cls.db_path = cls.tf.name
        cls.tf.close()

        # db_proxyをリセット
        from src.database_factory import DatabaseFactory

        DatabaseFactory.reset()

        cls.db = StockDatabase(cls.db_path)

        # テストデータ
        stocks = [
            {
                "code": "2001",
                "name": "Fetcher Stock A",
                "sector": "Tech",
                "market": "Prime",
            },
            {
                "code": "2002",
                "name": "Fetcher Stock B",
                "sector": "Fin",
                "market": "Standard",
            },
        ]
        cls.db.upsert_stocks(stocks)

        market_data = [
            {
                "code": "2001",
                "entry_date": "2025-02-01",
                "price": 500,
                "per": 10.0,
                "pbr": 0.8,
            },
            {
                "code": "2001",
                "entry_date": "2025-02-02",
                "price": 510,
                "per": 10.2,
                "pbr": 0.82,
            },
            {
                "code": "2002",
                "entry_date": "2025-02-01",
                "price": 750,
                "per": 12.0,
                "pbr": 1.1,
            },
            {
                "code": "2002",
                "entry_date": "2025-02-02",
                "price": 760,
                "per": 12.2,
                "pbr": 1.12,
            },
        ]
        cls.db.upsert_market_data(market_data)

        # DataFetcher用のconfig
        cls.config = {"paths": {"db_file": cls.db_path}}

    @classmethod
    def tearDownClass(cls):
        """テスト終了後のクリーンアップ"""
        from src.database_factory import DatabaseFactory

        DatabaseFactory.reset()
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_fetcher_single_code(self):
        """DataFetcher経由での単一銘柄取得"""
        fetcher = DataFetcher(self.config)
        df = fetcher.fetch_data_from_db(["2001"])

        self.assertFalse(df.empty)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["code"], "2001")
        self.assertEqual(df.iloc[0]["price"], 510)  # 最新日

    def test_fetcher_multiple_codes(self):
        """DataFetcher経由での複数銘柄取得"""
        fetcher = DataFetcher(self.config)
        df = fetcher.fetch_data_from_db(["2001", "2002"])

        self.assertEqual(len(df), 2)
        codes = df["code"].tolist()
        self.assertIn("2001", codes)
        self.assertIn("2002", codes)

    def test_fetcher_nonexistent_code(self):
        """DataFetcher経由での存在しない銘柄"""
        fetcher = DataFetcher(self.config)
        df = fetcher.fetch_data_from_db(["8888"])

        self.assertTrue(df.empty)


@pytest.mark.integration
class TestBaseFeatures_LargeScaleScenario(unittest.TestCase):
    """大規模シナリオテスト：多数の銘柄と長期間のデータ"""

    @classmethod
    def setUpClass(cls):
        """100銘柄 x 30日分のデータを生成"""
        cls.tf = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        cls.db_path = cls.tf.name
        cls.tf.close()

        from src.database_factory import DatabaseFactory

        DatabaseFactory.reset()

        cls.db = StockDatabase(cls.db_path)

        # 100銘柄
        stocks = []
        for i in range(100):
            stocks.append(
                {
                    "code": f"{3000 + i}",
                    "name": f"Large Scale Stock {i}",
                    "sector": "Test",
                    "market": "Prime",
                }
            )
        cls.db.upsert_stocks(stocks)

        # 各銘柄に30日分のデータ
        base_date = datetime(2025, 1, 1)
        market_data = []
        for i in range(100):
            code = f"{3000 + i}"
            for day in range(30):
                entry_date = (base_date + timedelta(days=day)).strftime("%Y-%m-%d")
                market_data.append(
                    {
                        "code": code,
                        "entry_date": entry_date,
                        "price": 1000 + i + day,
                        "per": 15.0,
                        "pbr": 1.0,
                    }
                )
        cls.db.upsert_market_data(market_data)

    @classmethod
    def tearDownClass(cls):
        from src.database_factory import DatabaseFactory

        DatabaseFactory.reset()
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_large_batch_performance(self):
        """100銘柄の一括取得"""
        codes = [f"{3000 + i}" for i in range(100)]

        import time

        start = time.time()
        df = self.db.get_market_data_batch(codes)
        elapsed = time.time() - start

        self.assertEqual(len(df), 100)
        # パフォーマンス要件: 100銘柄の取得が1秒以内
        self.assertLess(elapsed, 1.0, f"Batch fetch took too long: {elapsed:.2f}s")

        # 全て最新日（2025-01-30）のデータであること
        for _, row in df.iterrows():
            self.assertEqual(row["entry_date"], "2025-01-30")

    def test_partial_batch_fetch(self):
        """50銘柄のみ取得"""
        codes = [f"{3000 + i}" for i in range(50)]
        df = self.db.get_market_data_batch(codes)

        self.assertEqual(len(df), 50)


if __name__ == "__main__":
    unittest.main()

import os
import unittest
from datetime import datetime

from peewee import SqliteDatabase
from src.database import StockDatabase
from src.models import AnalysisResult, MarketData, Stock, db_proxy


class TestStockDatabase(unittest.TestCase):
    def setUp(self):
        """テスト用の一時DBファイルを作成し、Proxyを初期化"""
        import time

        self.test_db_path = f"data/test_db_unit_{int(time.time()*1000)}.db"

        # 初期化 (Force initialize db_proxy to use the temporary test DB)
        test_db = SqliteDatabase(self.test_db_path)
        db_proxy.initialize(test_db)
        self.db = StockDatabase(self.test_db_path)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        try:
            db_proxy.close()
        except Exception:
            pass
        if os.path.exists(self.test_db_path):
            import time

            time.sleep(0.1)
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    def test_init_db(self):
        """テーブル作成のテスト"""
        # Peewee 経由でテーブルが存在するか確認
        self.assertTrue(Stock.table_exists())
        self.assertTrue(MarketData.table_exists())
        self.assertTrue(AnalysisResult.table_exists())

        # Raw SQL でも確認 (テストは分離されたDBで実行)
        tables = db_proxy.get_tables()
        # 少なくとも主要テーブルが存在することを確認
        self.assertTrue(len(tables) >= 3, f"Expected at least 3 tables, got {tables}")

    def test_upsert_stocks(self):
        """銘柄マスタの登録・更新テスト"""
        stocks = [
            {"code": "7203", "name": "Toyota", "sector": "Car", "market": "Prime"},
            {
                "code": "9984",
                "name": "Softbank",
                "sector": "Telecom",
                "market": "Prime",
            },
        ]
        self.db.upsert_stocks(stocks)

        # 取得テスト
        s = self.db.get_stock("7203")
        self.assertEqual(s["name"], "Toyota")

        # 更新テスト
        updated_stocks = [
            {"code": "7203", "name": "Toyota New", "sector": "Car", "market": "Prime"}
        ]
        self.db.upsert_stocks(updated_stocks)
        s_updated = self.db.get_stock("7203")
        self.assertEqual(s_updated["name"], "Toyota New")

    def test_upsert_market_data(self):
        """市況データの登録・更新テスト"""
        today = datetime.now().strftime("%Y-%m-%d")
        # First create stocks (FK requirement)
        self.db.upsert_stocks(
            [
                {"code": "7203", "name": "Toyota", "sector": "Car", "market": "Prime"},
                {
                    "code": "9984",
                    "name": "Softbank",
                    "sector": "Telecom",
                    "market": "Prime",
                },
            ]
        )
        data = [
            {
                "code": "7203",
                "price": 2500,
                "per": 10.5,
                "roe": 12.0,
                "entry_date": today,
            },
            {"code": "9984", "price": 6000, "entry_date": today},
        ]
        self.db.upsert_market_data(data)

        # ステータス確認
        status = self.db.get_market_data_status(today)
        self.assertIn("7203", status)
        self.assertIn("9984", status)

        # 重複登録での更新テスト
        m_id = self.db.get_market_data_id("7203", today)
        data_update = [{"code": "7203", "price": 2600, "entry_date": today}]
        self.db.upsert_market_data(data_update)

        # Peewee で確認
        record = MarketData.get_by_id(m_id)
        self.assertEqual(record.price, 2600)

    def test_save_and_cache_analysis(self):
        """分析結果の保存とキャッシュ取得テスト"""
        today = datetime.now().strftime("%Y-%m-%d")
        # 前提データ (stock + market_data)
        self.db.upsert_stocks(
            [{"code": "7203", "name": "Toyota", "sector": "Car", "market": "Prime"}]
        )
        self.db.upsert_market_data(
            [{"code": "7203", "price": 2500, "entry_date": today}]
        )
        m_id = self.db.get_market_data_id("7203", today)

        record = {
            "market_data_id": m_id,
            "strategy_name": "Value_v1",
            "quant_score": 80,
            "ai_sentiment": "Bullish",
            "ai_reason": "Good growth",
            "ai_risk": "Low",
            "row_hash": "hash_v1",
        }
        self.db.save_analysis_result(record)

        # キャッシュ取得
        cache = self.db.get_ai_cache("7203", "hash_v1", "Value_v1")
        self.assertIsNotNone(cache)
        self.assertEqual(cache["ai_sentiment"], "Bullish")
        self.assertEqual(cache["quant_score"], 80)

    def test_empty_inputs(self):
        """空の入力に対する安全性のテスト"""
        self.db.upsert_stocks([])
        self.db.upsert_market_data([])
        self.assertIsNone(self.db.get_stock("0000"))
        self.assertEqual(self.db.get_market_data_status("2000-01-01"), set())

    def test_error_handling_invalid_field(self):
        """不正なフィールドが含まれる場合のハンドリング"""
        # First create stock (FK requirement)
        self.db.upsert_stocks(
            [{"code": "7203", "name": "Toyota", "sector": "Car", "market": "Prime"}]
        )
        # upsert_market_data は内部でフィルタリングしているためエラーにならないはず
        data = [
            {"code": "7203", "entry_date": "2025-01-01", "non_existent_field": "value"}
        ]
        try:
            self.db.upsert_market_data(data)
        except Exception as e:
            self.fail(f"upsert_market_data failed with invalid field: {e}")


if __name__ == "__main__":
    unittest.main()

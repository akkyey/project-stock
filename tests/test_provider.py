import os
import tempfile
import unittest

from src.database import StockDatabase
from src.models import MarketData, Stock
from src.provider import DataProvider


class TestDataProvider(unittest.TestCase):
    def setUp(self):
        # グローバルなdb_proxyをクリーンアップ
        from src.database_factory import DatabaseFactory

        DatabaseFactory.reset()

        # Use unique temp DB file
        self.tf = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.test_db_path = self.tf.name
        self.tf.close()

        # StockDatabase経由で初期化 (db_proxyのパス追跡も更新される)
        self.db = StockDatabase(self.test_db_path)

        # 銘柄マスタ
        Stock.create(code="7777", name="Provider Test", sector="IT", market="Prime")

        # 市況データ (複数日付)
        MarketData.create(
            code="7777", entry_date="2025-01-01", price=100, fetch_status="success"
        )
        MarketData.create(
            code="7777", entry_date="2025-01-02", price=200, fetch_status="success"
        )

        self.config = {"paths": {"db_file": self.test_db_path}}
        self.provider = DataProvider(self.config)

    def tearDown(self):
        from src.database_factory import DatabaseFactory

        DatabaseFactory.reset()
        if os.path.exists(self.test_db_path):
            import time

            time.sleep(0.1)  # Allow file handles to close
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    def test_load_latest_market_data(self):
        df = self.provider.load_latest_market_data()
        self.assertFalse(df.empty)
        # 1銘柄のみ、かつ最新の日付 (200円) が取得されていること
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["current_price"], 200)
        self.assertEqual(df.iloc[0]["code"], "7777")

    def test_get_ai_cache_and_save(self):
        # データ準備
        row_dict = {
            "code": "7777",
            "market_data_id": 1,
            "current_price": 200,
            "per": 10,
            "pbr": 1,
            "roe": 10,
            "dividend_yield": 3,
            "quant_score": 75,
        }
        strategy = "test_strategy"

        # キャッシュ取得 (最初は None)
        cached, row_hash = self.provider.get_ai_cache(row_dict, strategy)
        self.assertIsNone(cached)
        self.assertIsNotNone(row_hash)

        # 保存
        result = row_dict.copy()
        result.update(
            {
                "ai_sentiment": "Bullish",
                "ai_reason": "Test reason",
                "ai_risk": "None",
                "row_hash": row_hash,
            }
        )
        self.provider.save_analysis_result(result, strategy)

        # 再度キャッシュ取得 (今度は存在するはず)
        cached2, hash2 = self.provider.get_ai_cache(row_dict, strategy)
        self.assertIsNotNone(cached2)
        self.assertEqual(cached2["ai_sentiment"], "Bullish")
        self.assertEqual(hash2, row_hash)


if __name__ == "__main__":
    unittest.main()

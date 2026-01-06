import unittest
from unittest.mock import patch

from peewee import SqliteDatabase
from src.commands.reset import ResetCommand
from src.models import AnalysisResult, MarketData, Stock, db_proxy

# Use in-memory database for testing
test_db = SqliteDatabase(":memory:")


class TestResetCommand(unittest.TestCase):
    def setUp(self):
        # Bind models to test DB
        db_proxy.initialize(test_db)
        test_db.create_tables([Stock, MarketData, AnalysisResult])

        # Patch StockDatabase in Provider to prevent re-init
        self.patcher = patch("src.provider.StockDatabase")
        self.MockDB = self.patcher.start()
        # Ensure the mock returns something reasonable if accessed, though ResetCommand mostly uses Model directly
        self.MockDB.return_value.db = test_db

        self.config = {"strategies": {"test_strategy": {}}}
        self.cmd = ResetCommand(self.config, debug_mode=True)

        # Setup test data
        s1 = Stock.create(code="1001", name="Test1", sector="Tech", market="TSE")
        s2 = Stock.create(code="2001", name="Test2", sector="Retail", market="TSE")

        md1 = MarketData.create(code=s1, entry_date="2025-01-01")
        md2 = MarketData.create(code=s2, entry_date="2025-01-01")

        AnalysisResult.create(
            market_data=md1, strategy_name="test_strategy", audit_version=1
        )
        AnalysisResult.create(
            market_data=md2, strategy_name="test_strategy", audit_version=1
        )
        AnalysisResult.create(
            market_data=md1, strategy_name="other_strategy", audit_version=2
        )

    def tearDown(self):
        self.patcher.stop()
        test_db.drop_tables([Stock, MarketData, AnalysisResult])
        test_db.close()

    def test_reset_by_strategy(self):
        self.cmd.execute(strategy="test_strategy")

        # Check results
        results = AnalysisResult.select().where(
            AnalysisResult.strategy_name == "test_strategy"
        )
        for r in results:
            self.assertIsNone(r.audit_version)

        # Other strategy should remain
        other = AnalysisResult.get(AnalysisResult.strategy_name == "other_strategy")
        self.assertEqual(other.audit_version, 2)

    def test_reset_by_code(self):
        # Reset 1001 only (across all strategies?)
        self.cmd.execute(code="1001")

        # md1 (1001) records should be reset
        subquery = (
            MarketData.select(MarketData.id).join(Stock).where(Stock.code == "1001")
        )
        res1 = AnalysisResult.select().where(AnalysisResult.market_data.in_(subquery))
        self.assertTrue(res1.count() > 0)
        for r in res1:
            self.assertIsNone(r.audit_version)

        # md2 (2001) should NOT be reset
        sub_md2 = (
            MarketData.select(MarketData.id).join(Stock).where(Stock.code == "2001")
        )
        res2 = AnalysisResult.get(AnalysisResult.market_data.in_(sub_md2))
        self.assertEqual(res2.audit_version, 1)

    def test_reset_by_both(self):
        self.cmd.execute(strategy="test_strategy", code="1001")

        # Exact match
        sub = MarketData.select(MarketData.id).join(Stock).where(Stock.code == "1001")
        r = (
            AnalysisResult.select()
            .where(
                (AnalysisResult.market_data.in_(sub))
                & (AnalysisResult.strategy_name == "test_strategy")
            )
            .get()
        )
        self.assertIsNone(r.audit_version)

        # Other strategy same code should NOT be reset
        r_other = (
            AnalysisResult.select()
            .where(
                (AnalysisResult.market_data.in_(sub))
                & (AnalysisResult.strategy_name == "other_strategy")
            )
            .get()
        )
        self.assertEqual(r_other.audit_version, 2)

    def test_reset_all(self):
        self.cmd.execute(reset_all=True)
        count = (
            AnalysisResult.select()
            .where(AnalysisResult.audit_version.is_null(False))
            .count()
        )
        self.assertEqual(count, 0)

    def test_reset_no_args(self):
        with patch.object(self.cmd.logger, "error") as mock_err:
            self.cmd.execute()
            mock_err.assert_called_once()


if __name__ == "__main__":
    unittest.main()

import unittest

from src.validation_engine import ValidationEngine


class TestHardCutting(unittest.TestCase):
    def setUp(self):
        self.config = {"sector_policies": {"default": {"na_allowed": []}}}
        self.validator = ValidationEngine(self.config)

    def test_abnormal_detection(self):
        # 1. Normal data
        normal_data = {
            "code": "7203",
            "price": 2000,
            "equity_ratio": 40.0,
            "sales": 1000,
            "operating_cf": 150,
            "operating_margin": 10.0,
            "per": 15.0,
            "pbr": 1.2,
            "roe": 10.0,
            "payout_ratio": 30.0,
        }
        # is_abnormal, reasons = self.validator.is_abnormal(normal_data) # Deprecated
        # self.assertFalse(is_abnormal)

        is_valid, issues = self.validator.validate_stock_data(normal_data)
        self.assertTrue(is_valid)

        # 2. Insolvent (Equity Ratio < 0)
        insolvent_data = normal_data.copy()
        insolvent_data["equity_ratio"] = -5.0
        
        # [Fix] Expect new error code from StockAnalysisData
        is_valid, issues = self.validator.validate_stock_data(insolvent_data)
        self.assertFalse(is_valid)
        self.assertIn("equity_ratio_negative", "".join(issues))

        # 3. Severe OCF Drain
        drain_data = normal_data.copy()
        drain_data["operating_cf"] = -150  # -15% margin (sales=1000)
        drain_data["ocf_margin"] = -15.0   # [Fix] OCF margin must be provided
        
        is_valid, issues = self.validator.validate_stock_data(drain_data)
        self.assertFalse(is_valid)
        self.assertIn("operating_cf_extreme_negative", "".join(issues))


if __name__ == "__main__":
    unittest.main()

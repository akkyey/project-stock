import os
import sys
import tempfile
import unittest

import yaml

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config_loader import ConfigLoader


class TestConfigValidation(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file
        self.tmp_config = tempfile.NamedTemporaryFile(
            delete=False, mode="w", suffix=".yaml", encoding="utf-8"
        )

    def tearDown(self):
        os.unlink(self.tmp_config.name)

    def write_config(self, data):
        """Helper to write dict to temp yaml"""
        self.tmp_config.close()  # Close previous handle
        with open(self.tmp_config.name, "w", encoding="utf-8") as f:
            yaml.dump(data, f)

    def test_valid_config(self):
        valid_data = {
            "current_strategy": "value_strict",
            "data": {"jp_stock_list": "dummy.csv", "output_path": "out.csv"},
            "csv_mapping": {"col_map": {}, "numeric_cols": []},
            "ai": {
                "model_name": "test-model",
                "interval_sec": 1.0,
                "max_concurrency": 1,
            },
            "scoring": {},
            "strategies": {
                "value_strict": {
                    "default_style": "s",
                    "persona": "p",
                    "default_horizon": "h",
                    "base_score": 0,
                    "min_requirements": {},
                    "points": {},
                    "thresholds": {},
                }
            },
            "scoring_v2": {
                "styles": {"test": {"weight_fund": 0.5, "weight_tech": 0.5}}
            },
        }
        self.write_config(valid_data)
        try:
            ConfigLoader(self.tmp_config.name)
        except ValueError as e:
            self.fail(f"Valid config raised ValueError: {e}")

    def test_missing_section(self):
        # Missing 'ai'
        invalid_data = {
            "current_strategy": "value_strict",
            "data": {"jp_stock_list": "dummy.csv"},
            "csv_mapping": {"col_map": {}, "numeric_cols": []},
            # 'ai': missing
            "scoring": {},
            "strategies": {"value_strict": {}},
        }
        self.write_config(invalid_data)
        with self.assertRaises(ValueError) as cm:
            ConfigLoader(self.tmp_config.name)
        # Pydantic raises ValidationError wrapped in ValueError
        # Message should look like: "Invalid Configuration: 1 validation error ... ai Field required"
        err_msg = str(cm.exception)
        self.assertIn("ai", err_msg)
        self.assertIn("Field required", err_msg)

    def test_invalid_interval(self):
        invalid_data = {
            "current_strategy": "value_strict",
            "data": {"jp_stock_list": "dummy.csv"},
            "csv_mapping": {"col_map": {}, "numeric_cols": []},
            "ai": {
                "model_name": "t",
                "interval_sec": -5.0,  # Negative -> Error
                "max_concurrency": 1,
            },
            "scoring": {},
            "strategies": {
                "value_strict": {
                    "default_style": "s",
                    "persona": "p",
                    "default_horizon": "h",
                    "base_score": 0,
                    "min_requirements": {},
                    "points": {},
                    "thresholds": {},
                }
            },
        }
        self.write_config(invalid_data)
        with self.assertRaises(ValueError) as cm:
            ConfigLoader(self.tmp_config.name)

        err_msg = str(cm.exception)
        # Pydantic error for ge=0.0
        self.assertIn("interval_sec", err_msg)
        self.assertIn("Input should be greater than or equal to", err_msg)


if __name__ == "__main__":
    unittest.main()

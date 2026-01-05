"""
Tests for src/calc/strategies/*.py
Covers scoring logic for Turnaround and Generic strategies.
"""

import os
import sys
import unittest

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.calc.strategies.generic import GenericStrategy
from src.calc.strategies.turnaround import TurnaroundStrategy


def get_mock_config():
    return {
        "strategies": {
            "turnaround_spec": {
                "default_style": "turnaround_style",
                "persona": "Recovery Hunter",
                "default_horizon": "medium_term",
                "base_score": 10,
                "min_requirements": {},
                "points": {
                    "sales_growth": 30,
                    "profit_growth": 15,
                    "pbr": 25,
                    "trend_signal": 10,
                },
                "thresholds": {"sales_growth": 10.0, "profit_growth": 0.0, "pbr": 1.5},
            },
            "value_strict": {
                "default_style": "value_balanced",
                "persona": "Value Investor",
                "default_horizon": "long_term",
                "base_score": 50,
                "min_requirements": {"quant_score": 60},
                "points": {"per": 10, "roe": 15, "dividend_yield": 10},
                "thresholds": {"per": 15.0, "roe": 10.0, "dividend_yield": 3.0},
            },
        },
        "scoring_v2": {
            "styles": {
                "turnaround_style": {"weight_fund": 0.8, "weight_tech": 0.2},
                "value_balanced": {"weight_fund": 0.7, "weight_tech": 0.3},
            },
            "macro": {"sentiment": "neutral"},
        },
    }


class TestTurnaroundStrategy(unittest.TestCase):
    """Unit tests for TurnaroundStrategy scoring logic."""

    def test_calculate_score_basic(self):
        """Basic score calculation with good values."""
        config = get_mock_config()
        strategy = TurnaroundStrategy(config)

        df = pd.DataFrame(
            [
                {
                    "code": "1001",
                    "sales_growth": 15.0,  # > 10 -> +30
                    "profit_growth": 5.0,  # > 0 -> +15
                    "pbr": 1.0,  # <= 1.5 -> +25
                    "trend_up": 1,  # trend -> +10 (tech component)
                }
            ]
        )

        result = strategy.calculate_score(df)

        self.assertIn("quant_score", result.columns)
        self.assertIn("strategy_name", result.columns)

        # Expected:
        # score_value = 25 (pbr)
        # score_growth = 30 + 15 = 45
        # fund_total = base(10) + 25 + 45 = 80
        # score_trend = 50 + 10 = 60
        # final = 80 * 0.8 + 60 * 0.2 = 64 + 12 = 76
        self.assertAlmostEqual(result["quant_score"].iloc[0], 76.0, places=1)

    def test_calculate_score_with_nan(self):
        """Score calculation should handle NaN values gracefully."""
        config = get_mock_config()
        strategy = TurnaroundStrategy(config)

        df = pd.DataFrame(
            [
                {
                    "code": "1002",
                    "sales_growth": None,  # NaN
                    "profit_growth": "N/A",  # Invalid
                    "pbr": 1.2,  # Valid
                    "trend_up": None,
                }
            ]
        )

        result = strategy.calculate_score(df)

        # Should still return a score
        self.assertTrue(result["quant_score"].iloc[0] >= 0)
        self.assertEqual(result["strategy_name"].iloc[0], "turnaround_spec")

    def test_calculate_score_low_values(self):
        """Score should be low when conditions are not met."""
        config = get_mock_config()
        strategy = TurnaroundStrategy(config)

        df = pd.DataFrame(
            [
                {
                    "code": "1003",
                    "sales_growth": 5.0,  # < 10 -> 0
                    "profit_growth": -10.0,  # <= 0 -> 0
                    "pbr": 3.0,  # > 1.5 -> 0
                    "trend_up": 0,  # no trend -> -10
                }
            ]
        )

        result = strategy.calculate_score(df)

        # Expected:
        # score_value = 0
        # score_growth = 0
        # fund_total = 10 + 0 + 0 = 10
        # score_trend = 50 - 10 = 40
        # final = 10 * 0.8 + 40 * 0.2 = 8 + 8 = 16
        self.assertAlmostEqual(result["quant_score"].iloc[0], 16.0, places=1)


class TestGenericStrategy(unittest.TestCase):
    """Unit tests for GenericStrategy (value_strict etc.)."""

    def test_calculate_score_basic(self):
        """Basic score for Generic strategy."""
        config = get_mock_config()
        strategy = GenericStrategy(config, "value_strict")

        df = pd.DataFrame(
            [
                {
                    "code": "2001",
                    "per": 12.0,  # <= 15 -> +10
                    "roe": 15.0,  # >= 10 -> +15
                    "dividend_yield": 4.0,  # >= 3 -> +10
                    "trend_up": 1,
                }
            ]
        )

        result = strategy.calculate_score(df)

        self.assertIn("quant_score", result.columns)
        # Expected logic may vary based on metric category mapping
        # Just verify it returns a valid score
        self.assertTrue(result["quant_score"].iloc[0] >= 0)
        self.assertEqual(result["strategy_name"].iloc[0], "value_strict")

    def test_calculate_score_missing_columns(self):
        """Handle missing columns gracefully."""
        config = get_mock_config()
        strategy = GenericStrategy(config, "value_strict")

        df = pd.DataFrame(
            [
                {
                    "code": "2002",
                    "per": 10.0,
                    # Other columns missing
                }
            ]
        )

        result = strategy.calculate_score(df)

        # Should not raise, returns valid result
        self.assertIn("quant_score", result.columns)

    def test_calculate_score_vectorized(self):
        """Vectorized calculation for multiple rows."""
        config = get_mock_config()
        strategy = GenericStrategy(config, "value_strict")

        df = pd.DataFrame(
            [
                {"code": "3001", "per": 10.0, "roe": 20.0, "dividend_yield": 5.0},
                {
                    "code": "3002",
                    "per": 20.0,
                    "roe": 5.0,
                    "dividend_yield": 1.0,
                },  # Fails all
                {"code": "3003", "per": 14.0, "roe": 12.0, "dividend_yield": 3.5},
            ]
        )

        result = strategy.calculate_score(df)

        self.assertEqual(len(result), 3)
        # First row should have highest score
        self.assertTrue(result["quant_score"].iloc[0] > result["quant_score"].iloc[1])


if __name__ == "__main__":
    unittest.main()

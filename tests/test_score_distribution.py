import os
import sys
import unittest

import numpy as np
import pandas as pd

# Adjust path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock, patch

from src.engine import AnalysisEngine


class MockCalculator:
    def calc_v2_score(self, df, style=None, strategy_name=None):
        # Return dummy dataframe with preset quant_score
        # Assumes df has 'raw_val' to base score on
        res = df.copy()
        res["quant_score"] = df["raw_val"]
        res["score_long"] = 0
        res["score_short"] = 0
        res["score_gap"] = 0
        res["active_style"] = "test"
        return res


class TestScoreDistribution(unittest.TestCase):
    def setUp(self):
        config = {"strategies": {}, "filter": {}}
        self.engine = AnalysisEngine(config)

    @patch("src.calc.engine.ScoringEngine.get_strategy")
    def test_normalization(self, mock_get_strategy):
        # Setup Mock Strategy behavior
        mock_strategy = MagicMock()

        def side_effect(df):
            calc = MockCalculator()
            return calc.calc_v2_score(df)

        mock_strategy.calculate_score.side_effect = side_effect
        mock_get_strategy.return_value = mock_strategy

        # Create 1000 random scores: Mean 60, Std 20
        np.random.seed(42)
        raw_scores = np.random.normal(60, 20, 1000)

        df = pd.DataFrame({"code": range(1000), "raw_val": raw_scores})

        # Calculate
        result = self.engine.calculate_scores(df, strategy_name="test_strategy")

        # Check basic stats
        final_scores = result["quant_score"]
        mean = final_scores.mean()
        std = final_scores.std()

        print(
            f"\n[Validation] Input Mean={raw_scores.mean():.2f}, Std={raw_scores.std():.2f}"
        )
        print(f"[Validation] Output Mean={mean:.2f}, Std={std:.2f}")

        self.assertTrue(59.0 < mean < 62.0, f"Mean should be approx 60, got {mean}")
        self.assertTrue(18.0 < std < 22.0, f"Std should be approx 20, got {std}")

    @patch("src.calc.engine.ScoringEngine.get_strategy")
    def test_zero_std(self, mock_get_strategy):
        # Setup Mock Strategy
        mock_strategy = MagicMock()

        def side_effect(df):
            calc = MockCalculator()
            return calc.calc_v2_score(df)

        mock_strategy.calculate_score.side_effect = side_effect
        mock_get_strategy.return_value = mock_strategy

        # All scores identical
        df = pd.DataFrame({"code": range(10), "raw_val": [50.0] * 10})
        result = self.engine.calculate_scores(df, strategy_name="test_strategy")

        self.assertTrue(
            all(result["quant_score"] == 50.0),
            "All scores should be 50 if input std is 0",
        )


if __name__ == "__main__":
    unittest.main()

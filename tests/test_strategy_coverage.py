import unittest

import pandas as pd

from src.calc.strategies.base import BaseStrategy
from src.calc.strategies.turnaround import TurnaroundStrategy


# Concrete implementation for testing BaseStrategy abstract class
class ConcreteStrategy(BaseStrategy):
    def calculate_score(self, data: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame()


class TestBaseStrategy(unittest.TestCase):
    def setUp(self):
        self.config = {
            "scoring": {"lower_is_better": ["per", "pbr"]},
            "strategies": {"test_strat": {"points": {}, "thresholds": {}}},
        }
        self.strategy = ConcreteStrategy(self.config)

    def test_safe_float(self):
        self.assertEqual(self.strategy._safe_float("1,000"), 1000.0)
        self.assertEqual(self.strategy._safe_float("50%"), 50.0)
        self.assertIsNone(self.strategy._safe_float(None))
        self.assertIsNone(self.strategy._safe_float("invalid"))

    def test_evaluate_metric_scalar(self):
        # RSI
        self.assertTrue(self.strategy._evaluate_metric_scalar("rsi_oversold", 30, 30))
        self.assertFalse(self.strategy._evaluate_metric_scalar("rsi_oversold", 31, 30))
        self.assertTrue(self.strategy._evaluate_metric_scalar("rsi_overbought", 70, 70))

        # Lower is better (per defined in setup)
        self.assertTrue(self.strategy._evaluate_metric_scalar("per", 10, 15))
        self.assertFalse(self.strategy._evaluate_metric_scalar("per", 20, 15))

        # Higher is better (default)
        self.assertTrue(self.strategy._evaluate_metric_scalar("roe", 10, 10))
        self.assertFalse(self.strategy._evaluate_metric_scalar("roe", 9, 10))

    def test_evaluate_metric_vectorized(self):
        vals = pd.Series([20, 40, 60])

        # RSI Oversold (<= 30)
        res = self.strategy._evaluate_metric_vectorized("rsi_oversold", vals, 30)
        self.assertTrue(res[0])
        self.assertFalse(res[1])

        # Lower is better (<= th & > 0)
        vals_mixed = pd.Series([10, 20, -5])
        res = self.strategy._evaluate_metric_vectorized("per", vals_mixed, 15)
        self.assertTrue(res[0])  # 10 <= 15
        self.assertFalse(res[1])  # 20 > 15
        self.assertFalse(res[2])  # -5 (ignored as usually invalid for valuation?)
        # Note: base.py logic for lower_is_better: (vals <= th) & (vals > 0)

    def test_calc_dividend_points_scalar(self):
        # Normal
        row = {"payout_ratio": 30, "operating_cf": 100}
        self.assertEqual(self.strategy._calc_dividend_points_scalar(row, 10), 10)

        # OCF Penalty (Negative OCF -> 0 points)
        row_neg_ocf = {"payout_ratio": 30, "operating_cf": -100}
        self.assertEqual(self.strategy._calc_dividend_points_scalar(row_neg_ocf, 10), 0)

        # Payout Penalty (> 100% -> deduct 20)
        row_high_payout = {"payout_ratio": 150, "operating_cf": 100}
        self.assertEqual(
            self.strategy._calc_dividend_points_scalar(row_high_payout, 10), -10
        )

    def test_calc_dividend_points_vectorized(self):
        df = pd.DataFrame(
            {"operating_cf": [100, -100, 100], "payout_ratio": [30, 30, 150]}
        )
        condition = pd.Series([True, True, True])
        pts = 10

        scores = self.strategy._calc_dividend_points_vectorized(df, condition, pts)

        self.assertEqual(scores[0], 10)  # Normal
        self.assertEqual(scores[1], 0)  # Neg OCF
        self.assertEqual(scores[2], -10)  # High Payout (10 - 20)


class TestTurnaroundStrategy(unittest.TestCase):
    def setUp(self):
        self.config = {
            "scoring_v2": {
                "styles": {
                    "turnaround_style": {"weight_fund": 0.8, "weight_tech": 0.2}
                },
                "tech_points": {"macd_bullish": 5, "rsi_oversold": 5},
            },
            "strategies": {
                "turnaround_spec": {
                    "points": {
                        "sales_growth": 30,
                        "profit_growth": 15,
                        "pbr": 25,
                        "roe": 20,
                        "roe_missing_penalty": 10,
                        "trend_signal": 10,
                    },
                    "thresholds": {
                        "sales_growth": 10.0,
                        "profit_growth": 0.0,
                        "pbr": 1.5,
                        "roe": 10.0,
                    },
                    "base_score": 10,
                }
            },
        }
        self.strategy = TurnaroundStrategy(self.config)

    def test_calculate_score_vectorized_full_scenario(self):
        df = pd.DataFrame(
            {
                "sales_growth": [20.0, 5.0, 20.0, 20.0],
                "profit_growth": [10.0, -10.0, 10.0, 10.0],
                "pbr": [1.0, 2.0, 1.0, 1.0],
                "roe": [15.0, None, 15.0, 15.0],  # Row 1 has missing ROE
                "trend_up": [1, 0, 1, 1],
                "macd_hist": [1.0, -1.0, 1.0, 1.0],
                "rsi_14": [25, 50, 25, 25],
                "turnaround_status": [None, "fall_red", "turnaround_black", None],
                "profit_status": [None, "crash", "surge", None],
            }
        )

        result = self.strategy.calculate_score(df)

        # Row 0: Perfect
        # Base: 10
        # Growth: Sales(30) + Profit(15) + ROE(20) = 65
        # Value: PBR(25) = 25
        # Fund Total: 10+65+25 = 100
        # Trend: Trend(10) + MACD(5) + RSI(5) = 20 + 50(base)? No, base trend is 50.
        # Trend init 50. +10(up) +5(macd) +5(rsi) = 70.
        # Final: (100*0.8) + (70*0.2) = 80 + 14 = 94.
        # Check: trend_up=1 -> +10. 50+10=60.
        # Code: score_trend += np.where(val == 1, pts, -pts). pts=10. so +10 or -10.
        # 50 + 10 = 60.
        # MACD: >0 -> +5. 65.
        # RSI: <=30 -> +5. 70.
        # Correct.
        self.assertAlmostEqual(result.iloc[0]["quant_score"], 94.0)

        # Row 1: Bad + Missing ROE + Penalty statuses
        # Base: 10
        # Growth: Sales(0) + Profit(0) + ROE(0) = 0.
        # Value: PBR(0).
        # Fund Total: 10.
        # Trend: 50 -10(trend) +0(macd) +0(rsi) = 40.
        # Penalty: ROE(10).
        # Status Penalty: fall_red(15) + crash(15) = 30.
        # Total Penalty = 10 + 30 = 40.
        # Score Status: fall_red(-15 from final), crash(-15 from final).
        # Final: (10*0.8) + (40*0.2) = 8 + 8 = 16.
        # 16 - 30(penalty in calculation?) - 15 - 15 ?
        # Code:
        # final_score = (Fund*W + Trend*W) - score_penalty.
        # final_score += ... (bonus/malus from status)
        # score_penalty += ... (just for recording?)
        # Wait, if 'turnaround_status' == 'fall_red': final_score += -15. score_penalty += 15.
        # So it subtracts 15 AND records it as penalty. It does NOT subtract penalty twice.
        # But ROE penalty IS subtracted from final_score equation: `... - score_penalty`.
        # So ROE penalty (10) is subtracted.
        # Then `fall_red`: final_score -= 15. (penalty += 15 for display).
        # `crash`: final_score -= 15.
        # So: 16 - 10(ROE) - 15(fall) - 15(crash) = -24 -> clipped to 0.
        self.assertEqual(result.iloc[1]["quant_score"], 0.0)
        self.assertEqual(result.iloc[1]["score_penalty"], 40.0)  # 10+15+15

    def test_calculate_score_scalar_scenarios(self):
        row = {
            "sales_growth": 20.0,
            "profit_growth": 10.0,
            "pbr": 1.0,
            "roe": 15.0,
            "trend_up": 1,
            "macd_hist": 1.0,
            "rsi_14": 25,
            "turnaround_status": "turnaround_black",
            "profit_status": "surge",
        }
        res = self.strategy.calculate_score_scalar(row)
        # Should be similar to vectorized Row 2 logic (perfect + bonuses)
        # Base 94 (from previous calc).
        # Bonuses: turnaround_black(+20), surge(+10).
        # 94 + 20 + 10 = 124 -> 100.
        self.assertEqual(res["quant_score"], 100.0)

        # Missing ROE scalar
        row_missing_roe = row.copy()
        row_missing_roe["roe"] = None
        res_roe = self.strategy.calculate_score_scalar(row_missing_roe)
        # Penalty 10. Lost ROE points(20).
        # Net change: -20(points) -10(penalty from final).
        # Fund change: -20 growth.
        # Fund was 100. Now 80.
        # Trend 70.
        # Weighted: (80*0.8) + (70*0.2) = 64 + 14 = 78.
        # Minus Penalty 10 = 68.
        # Plus Bonuses 30 = 98.
        self.assertEqual(res_roe["quant_score"], 98.0)

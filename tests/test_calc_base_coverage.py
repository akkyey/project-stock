# -*- coding: utf-8 -*-
"""
src/calc/base.py と src/calc/strategies/__init__.py のカバレッジ向上テスト
"""
import unittest

import numpy as np
import pandas as pd

from src.calc.base import BaseCalculator
from src.calc.strategies import get_strategy
from src.calc.strategies.generic import GenericStrategy
from src.calc.strategies.growth_quality import GrowthQualityStrategy
from src.calc.strategies.turnaround import TurnaroundStrategy
from src.calc.strategies.value_growth_hybrid import ValueGrowthHybridStrategy
from src.calc.strategies.value_strict import ValueStrictStrategy


class TestBaseCalculatorCoverage(unittest.TestCase):
    """BaseCalculator のカバレッジ向上テスト"""

    def setUp(self):
        self.config = {
            "strategies": {"test_strat": {"lower_is_better": ["per", "pbr"]}},
            "current_strategy": "test_strat",
        }
        self.calc = BaseCalculator(self.config)

    def test_evaluate_metric_vectorized_rsi_oversold(self):
        """RSI oversold 条件のベクトル評価 (lines 32-33)"""
        vals = pd.Series([20, 30, 40, 50])
        result = self.calc._evaluate_metric_vectorized("rsi_oversold", vals, 30)
        expected = pd.Series([True, True, False, False])
        pd.testing.assert_series_equal(result, expected)

    def test_evaluate_metric_vectorized_rsi_overbought(self):
        """RSI overbought 条件のベクトル評価 (lines 34-35)"""
        vals = pd.Series([60, 70, 80, 90])
        result = self.calc._evaluate_metric_vectorized("rsi_overbought", vals, 70)
        expected = pd.Series([False, True, True, True])
        pd.testing.assert_series_equal(result, expected)

    def test_evaluate_metric_vectorized_lower_is_better(self):
        """lower_is_better 指標のベクトル評価 (lines 36-37)"""
        vals = pd.Series([10, 15, 20, 25])
        result = self.calc._evaluate_metric_vectorized("per", vals, 15)
        expected = pd.Series([True, True, False, False])
        pd.testing.assert_series_equal(result, expected)

    def test_evaluate_metric_vectorized_higher_is_better(self):
        """通常指標（高いほど良い）のベクトル評価 (lines 38-39)"""
        vals = pd.Series([5, 10, 15, 20])
        result = self.calc._evaluate_metric_vectorized("roe", vals, 10)
        expected = pd.Series([False, True, True, True])
        pd.testing.assert_series_equal(result, expected)

    def test_evaluate_metric_scalar_rsi_oversold(self):
        """RSI oversold スカラー評価 (line 43)"""
        self.assertTrue(self.calc._evaluate_metric_scalar("rsi_oversold", 25, 30))
        self.assertFalse(self.calc._evaluate_metric_scalar("rsi_oversold", 35, 30))

    def test_evaluate_metric_scalar_rsi_overbought(self):
        """RSI overbought スカラー評価 (line 44)"""
        self.assertTrue(self.calc._evaluate_metric_scalar("rsi_overbought", 75, 70))
        self.assertFalse(self.calc._evaluate_metric_scalar("rsi_overbought", 65, 70))

    def test_evaluate_metric_scalar_lower_is_better(self):
        """lower_is_better スカラー評価 (line 45)"""
        self.assertTrue(self.calc._evaluate_metric_scalar("per", 10, 15))
        self.assertFalse(self.calc._evaluate_metric_scalar("per", 20, 15))

    def test_evaluate_metric_scalar_higher_is_better(self):
        """通常指標スカラー評価 (line 46)"""
        self.assertTrue(self.calc._evaluate_metric_scalar("roe", 15, 10))
        self.assertFalse(self.calc._evaluate_metric_scalar("roe", 5, 10))

    def test_calc_dividend_points_vectorized_basic(self):
        """配当ポイント計算（基本条件） (lines 50-62)"""
        df = pd.DataFrame(
            {"operating_cf": [100, -50, 200], "payout_ratio": [50, 60, 150]}
        )
        condition = pd.Series([True, True, True])
        pts = 20

        result = self.calc._calc_dividend_points_vectorized(df, condition, pts)
        # Row 0: pts=20 (CF+, payout OK)
        # Row 1: pts=0 (CF < 0)
        # Row 2: pts=0 (payout > 100 -> 20-20=0)
        expected = np.array([20, 0, 0])
        np.testing.assert_array_equal(result, expected)

    def test_calc_dividend_points_vectorized_no_cf_column(self):
        """operating_cf列がない場合 (line 53)"""
        df = pd.DataFrame({"payout_ratio": [50, 60]})
        condition = pd.Series([True, True])
        result = self.calc._calc_dividend_points_vectorized(df, condition, 10)
        expected = np.array([10, 10])
        np.testing.assert_array_equal(result, expected)

    def test_calc_dividend_points_scalar_cf_negative(self):
        """スカラー版: 営業CF赤字時 (lines 66-69)"""
        row = {"operating_cf": -100, "payout_ratio": 50}
        result = self.calc._calc_dividend_points_scalar(row, 20)
        self.assertEqual(result, 0)

    def test_calc_dividend_points_scalar_payout_high(self):
        """スカラー版: 配当性向 > 100% (lines 71-73)"""
        row = {"operating_cf": 100, "payout_ratio": 120}
        result = self.calc._calc_dividend_points_scalar(row, 20)
        self.assertEqual(result, 0)  # 20 - 20 = 0

    def test_calc_dividend_points_scalar_normal(self):
        """スカラー版: 正常ケース (line 74)"""
        row = {"operating_cf": 100, "payout_ratio": 50}
        result = self.calc._calc_dividend_points_scalar(row, 20)
        self.assertEqual(result, 20)


class TestStrategyFactoryCoverage(unittest.TestCase):
    """src/calc/strategies/__init__.py の get_strategy カバレッジ"""

    def setUp(self):
        self.config = {"strategies": {}}

    def test_get_turnaround_strategy(self):
        """turnaround_spec 分岐 (lines 13-14)"""
        s = get_strategy("turnaround_spec", self.config)
        self.assertIsInstance(s, TurnaroundStrategy)

    def test_get_value_strict_strategy(self):
        """value_strict 分岐 (lines 15-16)"""
        s = get_strategy("value_strict", self.config)
        self.assertIsInstance(s, ValueStrictStrategy)

    def test_get_growth_quality_strategy(self):
        """growth_quality 分岐 (lines 17-18)"""
        s = get_strategy("growth_quality", self.config)
        self.assertIsInstance(s, GrowthQualityStrategy)

    def test_get_value_growth_hybrid_strategy(self):
        """value_growth_hybrid 分岐 (lines 19-20)"""
        s = get_strategy("value_growth_hybrid", self.config)
        self.assertIsInstance(s, ValueGrowthHybridStrategy)

    def test_get_generic_strategy_fallback(self):
        """未知の戦略名はGenericにフォールバック (lines 22-23)"""
        s = get_strategy("unknown_strategy", self.config)
        self.assertIsInstance(s, GenericStrategy)


if __name__ == "__main__":
    unittest.main()

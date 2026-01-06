# tests/test_parallel_validation.py
"""
Tests for Parallel Validation and Scoring functionality
[v8.0] Performance verification for batch processing
"""
import os
import sys
import time
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config_loader import ConfigLoader
from src.validation_engine import ValidationEngine


class TestParallelValidation(unittest.TestCase):
    """Unit tests for parallel validation batch processing."""

    @classmethod
    def setUpClass(cls):
        cls.config = ConfigLoader().config
        cls.engine = ValidationEngine(cls.config)

    def _create_test_tasks(self, count: int) -> list:
        """Generate mock tasks for testing."""
        tasks = []
        for i in range(count):
            task = {
                "prompt": f"Stock Analysis for CODE{i:04d}\n"
                f"Price: {1000 + i} JPY\n"
                f"PER: {10 + (i % 20)}\n"
                f"PBR: {0.8 + (i % 10) * 0.1}\n"
                f"ROE: {8 + (i % 15)}\n"
                f"Debt/Equity Ratio: 0.5\n"
                f"Operating Margin: 10%\n"
                f"Free CF: 1000\n"
                f"Op CF Margin: 5%\n"
                f"Sales Growth: 5%\n"
                f"Profit Growth: 3%\n"
                f"Current Ratio: 150\n"
                f"Quick Ratio: 100\n",
                "sector": "サービス業" if i % 3 == 0 else "情報・通信業",
                "strategy": "value_strict",
                "score_value": 20,
                "score_growth": 15,
                "score_trend": 50,
            }
            tasks.append(task)
        return tasks

    def test_validate_batch_empty(self):
        """Empty batch should return empty list."""
        result = self.engine.validate_batch([])
        self.assertEqual(result, [])

    def test_validate_batch_single(self):
        """Single task should use sequential mode."""
        tasks = self._create_test_tasks(1)
        result = self.engine.validate_batch(tasks)

        self.assertEqual(len(result), 1)
        task, is_valid, reason = result[0]
        self.assertIsInstance(is_valid, bool)

    def test_validate_batch_parallel(self):
        """Multiple tasks should use parallel mode by default."""
        tasks = self._create_test_tasks(10)
        result = self.engine.validate_batch(tasks, max_workers=4)

        self.assertEqual(len(result), 10)
        # All results should be tuples
        for task, is_valid, reason in result:
            self.assertIsInstance(is_valid, bool)
            self.assertIsInstance(reason, str)

    def test_validate_batch_sequential_mode(self):
        """Forced sequential mode should work."""
        tasks = self._create_test_tasks(5)
        result = self.engine.validate_batch(tasks, use_parallel=False)

        self.assertEqual(len(result), 5)

    def test_validate_batch_result_order_preserved(self):
        """Parallel processing should preserve result order."""
        tasks = self._create_test_tasks(20)
        result = self.engine.validate_batch(tasks, max_workers=4)

        # Check that indices match
        for i, (task, is_valid, reason) in enumerate(result):
            expected_code = f"CODE{i:04d}"
            self.assertIn(expected_code, task["prompt"])


class TestParallelPerformance(unittest.TestCase):
    """Performance benchmarks for parallel vs sequential processing."""

    @classmethod
    def setUpClass(cls):
        cls.config = ConfigLoader().config
        cls.engine = ValidationEngine(cls.config)

    def _create_test_tasks(self, count: int) -> list:
        """Generate mock tasks."""
        tasks = []
        for i in range(count):
            task = {
                "prompt": f"Stock CODE{i:04d}\nPrice: {1000 + i} JPY\n"
                f"PER: {10 + (i % 20)}\nPBR: 1.0\nROE: 10\n"
                f"Debt/Equity Ratio: 0.5\nOperating Margin: 10%\n"
                f"Free CF: 1000\nOp CF Margin: 5%\n"
                f"Sales Growth: 5%\nProfit Growth: 3%\n"
                f"Current Ratio: 150\nQuick Ratio: 100\n",
                "sector": "サービス業",
                "strategy": "value_strict",
                "score_value": 20,
                "score_growth": 15,
                "score_trend": 50,
            }
            tasks.append(task)
        return tasks

    def test_performance_comparison(self):
        """Compare sequential vs parallel performance."""
        task_count = 100
        tasks = self._create_test_tasks(task_count)

        # Sequential timing
        start = time.perf_counter()
        seq_result = self.engine.validate_batch(tasks, use_parallel=False)
        seq_time = time.perf_counter() - start

        # Parallel timing
        start = time.perf_counter()
        par_result = self.engine.validate_batch(tasks, max_workers=4, use_parallel=True)
        par_time = time.perf_counter() - start

        # Both should return same number of results
        self.assertEqual(len(seq_result), len(par_result))

        # Report results (not a hard assertion as performance varies)
        print(f"\n📊 Performance Comparison ({task_count} tasks):")
        print(f"   Sequential: {seq_time:.4f}s")
        print(f"   Parallel (4 workers): {par_time:.4f}s")
        print(f"   Speedup: {seq_time/par_time:.2f}x" if par_time > 0 else "   N/A")

        # Soft assertion: parallel should not be significantly slower
        # (on small workloads, overhead may make it slower)
        self.assertLessEqual(
            par_time, seq_time * 3, "Parallel should not be 3x slower than sequential"
        )


if __name__ == "__main__":
    unittest.main()

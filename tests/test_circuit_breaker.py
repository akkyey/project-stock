import unittest

from src.circuit_breaker import CircuitBreaker


class TestCircuitBreaker(unittest.TestCase):
    def test_initial_state(self):
        cb = CircuitBreaker(threshold=3)
        self.assertFalse(cb.check_abort_condition())
        self.assertEqual(cb.consecutive_429_errors, 0)

    def test_update_status_quota_error(self):
        cb = CircuitBreaker(threshold=2)

        # 1st Error (429)
        cb.update_status(
            {"ai_sentiment": "Error", "ai_reason": "API Quota Exceeded (429)"}
        )
        self.assertEqual(cb.consecutive_429_errors, 1)
        self.assertFalse(cb.check_abort_condition())

        # 2nd Error (429) -> Threshold reached
        cb.update_status(
            {"ai_sentiment": "Error", "ai_reason": "ResourceExhausted quota"}
        )
        self.assertEqual(cb.consecutive_429_errors, 2)
        self.assertTrue(cb.check_abort_condition())

    def test_update_status_reset(self):
        cb = CircuitBreaker(threshold=2)

        # 1st Error
        cb.update_status({"ai_sentiment": "Error", "ai_reason": "429 error"})
        self.assertEqual(cb.consecutive_429_errors, 1)

        # Success
        cb.update_status({"ai_sentiment": "Bullish", "ai_reason": "Good"})
        self.assertEqual(cb.consecutive_429_errors, 0)

    def test_other_error_does_not_count(self):
        cb = CircuitBreaker(threshold=2)

        # Network Error (not quota)
        cb.update_status({"ai_sentiment": "Error", "ai_reason": "Network timeout"})
        self.assertEqual(cb.consecutive_429_errors, 0)


if __name__ == "__main__":
    unittest.main()

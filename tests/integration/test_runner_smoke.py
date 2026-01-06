import os
import sys
import unittest
import tempfile

# Path resolution
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, "stock-analyzer4"))

from src.config_loader import load_config
from equity_auditor import EquityAuditor

class TestRunnerSmoke(unittest.TestCase):
    """[v7.5] End-to-End Smoke Tests for Runner"""

    def test_extract_smoke_all_strategies(self):
        print("\nTesting Runner EXTRACT mode for ALL strategies (Smoke Test)...")

        # Load real config
        # Currently in project-stock2 root
        config_path = os.path.join(base_dir, "config/config.yaml")
        if not os.path.exists(config_path):
             print("Skipping smoke test: config/config.yaml not found.")
             return

        config = load_config(config_path)
        strategies = list(config.get("strategies", {}).keys())

        if "turnaround_spec" not in strategies:
            strategies.append("turnaround_spec")

        print(f"  Target Strategies: {strategies}")

        runner = EquityAuditor(debug_mode=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            for strategy in strategies:
                output_file = os.path.join(temp_dir, f"smoke_{strategy}.json")
                print(f"  - Testing strategy: {strategy} ... ", end="")
                try:
                    # Run extract via command
                    # Need to ensure runner is initialized with correct config or paths if needed
                    # But EquityAuditor loads config internally.
                    # We might need to ensure CWD is correct or config path is correct for it.
                    # EquityAuditor uses "config/config.yaml" by default.
                    # Since we run pytest from project root, it should be fine.
                    
                    if strategy not in runner.config["strategies"] and strategy != "turnaround_spec":
                         print(f"Skipping {strategy} (not in loaded config)")
                         continue

                    # Guard against strategies that might fail if data is missing
                    # This is a smoke test, so we expect it to 'run', not necessarily find data.
                    runner.commands["extract"].execute(
                        strategy, limit=1, output_path=output_file
                    )

                    if os.path.exists(output_file):
                        print("OK (File created)")
                    else:
                        print("OK (No candidates/No file)")

                except Exception as e:
                    self.fail(f"Runner failed for strategy '{strategy}': {e}")

        print("Runner Smoke Test -> ALL OK")

if __name__ == "__main__":
    unittest.main()

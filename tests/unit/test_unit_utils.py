import os
import sys
import unittest

# Path resolution
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, "stock-analyzer4"))

from src.config_loader import ConfigLoader
from equity_auditor import EquityAuditor

class TestUtils(unittest.TestCase):
    def test_config_loader(self):
        print("\nTesting ConfigLoader...")
        config_path = "config/config.yaml"
        # We need to ensure we look from project-stock2 root
        # Start from base_dir determined above
        abs_config_path = os.path.join(base_dir, config_path)
        
        if os.path.exists(abs_config_path):
            loader = ConfigLoader(abs_config_path)
            self.assertIsInstance(loader.config, dict)
            print("OK (config.yaml found)")
        else:
            print(f"Skip (config.yaml not found at {abs_config_path})")

    def test_runner_init(self):
        """EquityAuditorの初期化テスト"""
        print("Testing EquityAuditor Init (V7+ Architecture)...")
        # equity_auditor.py depends on relative imports or path setup.
        # It is usually run as script.
        # Here we import it as module. Be careful about its internal imports.
        # It imports 'src.orchestrator', which should work given sys.path setup.
        
        runner = EquityAuditor(debug_mode=True)
        self.assertIn("extract", runner.commands)
        self.assertIn("analyze", runner.commands)
        self.assertIn("ingest", runner.commands)
        self.assertIn("reset", runner.commands)

        self.assertIsNotNone(runner.config)
        self.assertIsNotNone(runner.commands["extract"].provider)
        self.assertIsNotNone(runner.commands["analyze"].agent)

        print("Antigravity Runner Init -> OK")

if __name__ == "__main__":
    unittest.main()

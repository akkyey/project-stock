#!/usr/bin/env python3

import os
import sys

import pytest

if __name__ == "__main__":
    print("🚀 Running Modernized Test Suite via Pytest (CI Wrapper)...")

    # Ensure project root is in sys.path
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Add submodule path if source exists
    submodule_path = os.path.join(project_root, "stock-analyzer4")
    if os.path.exists(os.path.join(submodule_path, "src")):
        if submodule_path not in sys.path:
            sys.path.insert(0, submodule_path)
    else:
        print(f"⚠️  Warning: Submodule source not found at {submodule_path}/src")
        print("   Tests depending on the submodule will likely fail.")

    # Define test targets
    test_targets = []
    
    # Check Project Root Tests
    if os.path.exists(os.path.join(project_root, "tests/unit")):
        test_targets.append("tests/unit")
    if os.path.exists(os.path.join(project_root, "tests/integration")):
        test_targets.append("tests/integration")
        
    # Check Submodule Tests
    submodule_tests = os.path.join(project_root, "stock-analyzer4/tests/unit")
    if os.path.exists(submodule_tests):
        test_targets.append("stock-analyzer4/tests/unit")
    else:
        print(f"⚠️  Warning: Submodule tests not found at {submodule_tests}")

    if not test_targets:
        print("❌ No test directories found!")
        sys.exit(1)

    print(f"🎯 Test Targets: {test_targets}")

    # Run pytest
    # Return the exit code to the caller (e.g., CI system)
    sys.exit(pytest.main(test_targets))

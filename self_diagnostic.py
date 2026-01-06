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

    # Run pytest
    # Return the exit code to the caller (e.g., CI system)
    sys.exit(pytest.main(["tests/unit", "tests/integration"]))

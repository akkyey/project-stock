#!/usr/bin/env python3

import os
import sys

import pytest

import subprocess

if __name__ == "__main__":
    print("🚀 Running Modernized Test Suite via Pytest (CI Wrapper)...")

    project_root = os.path.dirname(os.path.abspath(__file__))
    exit_code = 0

    def run_suite(targets, cwd, description):
        """Run pytest on targets in the specific working directory."""
        if not targets:
            return 0
            
        print(f"\n🎯 Running {description}...")
        print(f"   Targets: {targets}")
        print(f"   CWD: {cwd}")
        
        # Build command: python3 -m pytest [targets]
        cmd = [sys.executable, "-m", "pytest"] + targets
        
        try:
            # We run pytest as a subprocess to isolate environments
            # passing the current env is usually fine, but CWD is key
            result = subprocess.run(cmd, cwd=cwd)
            return result.returncode
        except Exception as e:
            print(f"❌ Error running suite {description}: {e}")
            return 1

    # 1. Root Tests
    root_targets = []
    if os.path.exists(os.path.join(project_root, "tests/unit")):
        root_targets.append("tests/unit")
    if os.path.exists(os.path.join(project_root, "tests/integration")):
        root_targets.append("tests/integration")
    
    # Note: If root tests depend on submodule, we assuming running in root works
    # provided sys.path setup (which subprocess inherits or we assume pythonpath/conftest handles it)
    # Actually, root tests usually assume installed package or local path.
    # We might need to set PYTHONPATH for root tests if they rely on submodule src.
    # In the original script, we inserted submodule path. 
    # Let's set PYTHONPATH for child process if needed.
    
    root_env = os.environ.copy()
    submodule_path = os.path.join(project_root, "stock-analyzer4")
    if os.path.exists(os.path.join(submodule_path, "src")):
         # Add submodule to PYTHONPATH for root tests
         pypath = root_env.get("PYTHONPATH", "")
         root_env["PYTHONPATH"] = f"{submodule_path}:{pypath}"

    if root_targets:
        # Run root tests with modified env
        print(f"\n➡️  Running Project Root Tests...")
        cmd = [sys.executable, "-m", "pytest"] + root_targets
        res = subprocess.run(cmd, cwd=project_root, env=root_env)
        if res.returncode != 0:
            exit_code = res.returncode

    # 2. Submodule Tests
    # Run these INSIDE the submodule directory to resolve 'src' correctly
    submodule_targets = []
    submodule_tests_path = os.path.join(submodule_path, "tests/unit")
    if os.path.exists(submodule_tests_path):
        submodule_targets.append("tests/unit")
    
    if submodule_targets:
        rc = run_suite(submodule_targets, cwd=submodule_path, description="Submodule (stock-analyzer4) Tests")
        if rc != 0:
            exit_code = rc

    if not root_targets and not submodule_targets:
        print("❌ No test directories found!")
        sys.exit(1)

    print(f"\n✅ All Test Suites Completed. Final Exit Code: {exit_code}")
    sys.exit(exit_code)

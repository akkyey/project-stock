import os
import sys

# Ensure the core logic in stock-analyzer4 is discoverable by tests
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
submodule_root = os.path.join(project_root, "stock-analyzer4")

if submodule_root not in sys.path:
    sys.path.insert(0, submodule_root)

# Optional: Add src to path directly if needed (usually submodule root is enough if imports are 'from src...')
# if os.path.join(submodule_root, "src") not in sys.path:
#     sys.path.insert(0, os.path.join(submodule_root, "src"))

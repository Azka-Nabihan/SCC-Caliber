"""
Streamlit Community Cloud Entry Point for SCC-Caliber.
Directly invokes src/app/dashboard.py with sys.path properly configured.
"""
import runpy
import sys
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Execute the main dashboard
runpy.run_path(str(root_dir / "src" / "app" / "dashboard.py"), run_name="__main__")

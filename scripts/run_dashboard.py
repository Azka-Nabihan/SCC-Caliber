"""
Launcher script for Chandra Asri Single Pane of Glass (SPOG) Streamlit Dashboard.
Guarantees execution using the active Python virtual environment (Solution M6).
Usage: python scripts/run_dashboard.py
"""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
APP_PATH = BASE_DIR / "src" / "app" / "dashboard.py"


def main():
    if not APP_PATH.exists():
        print(f"Error: Dashboard entrypoint not found at {APP_PATH}")
        sys.exit(1)

    print("=" * 60)
    print("🚀 Launching Chandra Asri SPOG Dashboard (CALIBER 2026)")
    print(f"📍 Entrypoint: {APP_PATH}")
    print(f"🐍 Python Executable: {sys.executable}")
    print("=" * 60)

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_PATH),
        "--server.headless",
        "false",
        "--theme.base",
        "dark",
    ]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard shutdown cleanly.")
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

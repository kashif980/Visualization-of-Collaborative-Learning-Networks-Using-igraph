"""Simple starter script for FastAPI backend.

Run with: python backend_runner.py
"""
import sys
import subprocess
from pathlib import Path

# Run uvicorn with the app
subprocess.run(
    [sys.executable, "-m", "uvicorn", "backend.api:app", "--host", "127.0.0.1", "--port", "9620"],
    cwd=Path(__file__).parent
)

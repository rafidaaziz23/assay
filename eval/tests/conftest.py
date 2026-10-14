"""Make the repo root importable from tests under eval/tests/."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

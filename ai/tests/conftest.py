"""Make the repo root importable from tests under ai/tests/."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

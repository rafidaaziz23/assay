#!/usr/bin/env python3
"""Strict /goal gate for the Assay DEV3 overnight run.

Exit 0 ONLY when the whole DEV3 Days 0-2 scope is genuinely done:
  - .venv exists and `import ai` works
  - ai/tests and eval/tests (if present) pass under pytest
  - prompts/honeypot-catalog.json has >= 10 entries
  - ai/FIXTURES.md exists
  - every H0.x / H1.x / H2.x unit in docs/DEV3-OVERNIGHT-LOG.md is marked done (check)

Because the /goal loop runs gates BEFORE the judge, a RED gate makes it impossible
for the loop to stop early. Offline only (no model calls) so it never hits the
300s gate ceiling.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOG = REPO / "docs" / "DEV3-OVERNIGHT-LOG.md"
PY = REPO / ".venv" / "Scripts" / "python.exe"
DONE_MARK = "\u2705"  # check mark
TODO_MARK = "\u2b1c"  # white square
REQUIRED_DAYS = ("0", "1", "2")

failures: list[str] = []


def run(args: list[str]) -> int:
    return subprocess.run(args, cwd=str(REPO), capture_output=True, text=True).returncode


def main() -> int:
    if not PY.exists():
        failures.append(f"venv missing: {PY} (do unit H0.1)")
        return report()

    if run([str(PY), "-c", "import ai"]) != 0:
        failures.append("`import ai` failed (units H0.3+)")

    for sub in ("ai/tests", "eval/tests"):
        if (REPO / sub).is_dir():
            rc = subprocess.run(
                [str(PY), "-m", "pytest", sub, "-q"],
                cwd=str(REPO), capture_output=True, text=True,
            )
            if rc.returncode != 0:
                failures.append(f"pytest {sub} failed:\n{rc.stdout[-600:]}{rc.stderr[-300:]}")

    catalog = REPO / "prompts" / "honeypot-catalog.json"
    if not catalog.exists():
        failures.append("prompts/honeypot-catalog.json missing (unit H0.5)")
    else:
        data = json.loads(catalog.read_text(encoding="utf-8"))
        entries = data if isinstance(data, list) else (data.get("terms") or data.get("catalog") or [])
        if len(entries) < 10:
            failures.append(f"honeypot catalog has {len(entries)} entries, need >= 10")

    if not (REPO / "ai" / "FIXTURES.md").exists():
        failures.append("ai/FIXTURES.md missing (unit H0.3)")

    # Status-line check: every H0/H1/H2 unit must carry the done marker.
    if not LOG.exists():
        failures.append("docs/DEV3-OVERNIGHT-LOG.md missing")
    else:
        text = LOG.read_text(encoding="utf-8", errors="replace")
        units = re.findall(r"(H(\d)\.\d+)\s*([^\sA-Za-z0-9])", text)
        seen = {u: m for u, _d, m in units}
        required = [u for u, d, _m in units if d in REQUIRED_DAYS]
        missing = sorted({u for u in required if seen.get(u) != DONE_MARK})
        if not required:
            failures.append("no H0/H1/H2 units found in the log status line")
        elif missing:
            failures.append(f"{len(missing)} unit(s) not DONE: {', '.join(missing)}")

    return report()


def report() -> int:
    if failures:
        print("GATE RED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("GATE GREEN: DEV3 Days 0-2 complete, tests pass, evidence present")
    return 0


if __name__ == "__main__":
    sys.exit(main())

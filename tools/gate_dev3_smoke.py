#!/usr/bin/env python3
"""Per-unit smoke gate for the Assay DEV3 run (offline, deterministic, <300s).

Checks that the engine imports, unit tests pass, and the static artifacts exist.
Live model calls are NOT exercised here (they can exceed the 300s gate ceiling);
per-unit live evidence goes in docs/logs/DEV3-OVERNIGHT-LOG.md instead.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY = REPO / ".venv" / "Scripts" / "python.exe"

failures: list[str] = []


def main() -> int:
    if not PY.exists():
        print(f"GAGAL: venv belum ada: {PY}")
        print("       kerjakan unit H0.1 dulu (lihat docs/logs/DEV3-OVERNIGHT-BRIEF.md)")
        return 1

    if subprocess.run([str(PY), "-c", "import ai"], cwd=str(REPO)).returncode != 0:
        failures.append("`import ai` gagal")

    for sub in ("ai/tests", "eval/tests"):
        if (REPO / sub).is_dir():
            rc = subprocess.run([str(PY), "-m", "pytest", sub, "-q"],
                                cwd=str(REPO), capture_output=True, text=True)
            if rc.returncode != 0:
                failures.append(f"pytest {sub} gagal:\n{rc.stdout[-500:]}")

    cat = REPO / "prompts" / "honeypot-catalog.json"
    if not cat.exists():
        failures.append("prompts/honeypot-catalog.json belum ada (unit H0.5)")
    else:
        data = json.loads(cat.read_text(encoding="utf-8"))
        entries = data if isinstance(data, list) else (data.get("terms") or data.get("catalog") or [])
        if len(entries) < 10:
            failures.append(f"honeypot-catalog.json cuma {len(entries)} entri, butuh >= 10")

    if not (REPO / "ai" / "FIXTURES.md").exists():
        failures.append("ai/FIXTURES.md belum ada (unit H0.3)")

    if failures:
        print("GATE MERAH:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("GATE HIJAU")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Shared harness for the DEV3 eval scripts (threaded, small-n by default).

Every runner writes raw records to ``eval/results/<name>.jsonl`` (auditable, as the
research methodology requires) and a summary to ``eval/results/<name>.json``. Reports
must always carry ``n`` — no number without a sample size (DEV3-ROADMAP section 11).
"""
from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
RESULTS = REPO / "eval" / "results"
RESULTS.mkdir(exist_ok=True)


def run_cases(cases: list[dict], fn, workers: int = 5) -> list[dict]:
    """Run ``fn(case)`` over cases with a bounded thread pool, preserving no order."""
    out: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = {ex.submit(fn, c): c for c in cases}
        for fut in as_completed(futs):
            case = futs[fut]
            try:
                rec = fut.result()
            except Exception as exc:  # noqa: BLE001 - a failed case must not kill the run
                rec = {"id": case.get("id"), "response": f"__ERROR__ {type(exc).__name__}: {exc}"}
            rec.setdefault("id", case.get("id"))
            out.append(rec)
    out.sort(key=lambda r: str(r.get("id")))
    return out


def write_jsonl(name: str, records: list[dict]) -> Path:
    path = RESULTS / f"{name}.jsonl"
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records), encoding="utf-8")
    return path


def write_json(name: str, obj: dict) -> Path:
    path = RESULTS / f"{name}.json"
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def live() -> bool:
    from ai import _client
    return not _client.demo_mode() and bool(_client._keys())


def n_arg(default: int, argv: list[str]) -> int:
    """Parse ``--n <int>`` from argv (small-n default keeps the API budget bounded)."""
    if "--n" in argv:
        try:
            return max(1, int(argv[argv.index("--n") + 1]))
        except Exception:
            return default
    return default

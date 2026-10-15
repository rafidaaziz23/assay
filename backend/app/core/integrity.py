"""Integrity / Focus Mode rules (F11–F13, ADR 003).

Frozen decisions this module enforces:

* ``video_transmitted`` MUST be ``false``. Any payload carrying a blob is rejected —
  inference runs on-device and only boolean events reach the server (ADR 003 s2.2).
* Focus Mode is a *signal*, never a claim of anti-cheat (PRD risk R5). Backend sells
  it as an integrity flag, nothing more.
* Accessible Mode (camera off) -> ``assisted_unverified``, and the chapter score is
  STILL computed. That path must never become an error path (DEV 2 F11/F12).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..core.state_machine import UNLOCK_THRESHOLD

# enum frozen in API-CONTRACTS section 2.7
FOCUS_EVENT_TYPES = ("GAZE_DRIFT", "MULTIPLE_FACES", "TAB_BLUR", "CAMERA_OFF")

INTEGRITY_CLEAN = "clean"
INTEGRITY_ASSISTED = "assisted"
INTEGRITY_ASSISTED_UNVERIFIED = "assisted_unverified"

# Integrity flag -> chapter-score adjustment. Mirrors ai/core.INTEGRITY_ADJUSTMENT:
# focus is a small scoring dimension, never a gate (ADR 002 s2.4).
INTEGRITY_ADJUSTMENT = {
    INTEGRITY_CLEAN: 0,
    INTEGRITY_ASSISTED: -3,
    # Accessible Mode is neutral on purpose: a student who cannot run the camera must
    # not be penalised for accessibility (accessibility note, PRD risk R6).
    INTEGRITY_ASSISTED_UNVERIFIED: 0,
}


class VideoPayloadRejected(ValueError):
    """Raised when a focus payload tries to smuggle video/image data to the server."""


def _looks_like_blob(event: Dict[str, Any]) -> bool:
    """Heuristic: any bulky or binary-looking value in an event means a blob.

    The event schema is boolean + timestamps. A ``blob``/``frame``/``data``/``video``
    key, or any string long enough to be encoded media, is a contract violation.
    """
    for key, value in event.items():
        if key in ("blob", "frame", "frames", "image", "video", "data_url", "bytes"):
            return True
        if isinstance(value, (bytes, bytearray, memoryview)):
            return True
        if isinstance(value, str) and len(value) > 2048:
            return True
    return False


def validate_focus_payload(payload: Dict[str, Any]) -> None:
    """Reject anything that contradicts ``video_transmitted: false`` (ADR 003)."""
    if payload.get("video_transmitted") is True:
        raise VideoPayloadRejected(
            "video_transmitted must be false: inference is on-device (ADR 003 s2.2)"
        )
    events = payload.get("events") or []
    body = dict(payload)
    body.pop("events", None)
    if _looks_like_blob(body):
        raise VideoPayloadRejected("focus payload must carry no media blob")
    for event in events:
        if _looks_like_blob(event):
            raise VideoPayloadRejected("focus event must carry no media blob")


def summarize_events(events: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count per event type; the contract's summary keys are fixed."""
    summary = {"gaze_drift_count": 0, "multi_face_count": 0, "tab_blur_count": 0}
    for event in events or []:
        etype = event.get("type")
        if etype == "GAZE_DRIFT":
            summary["gaze_drift_count"] += 1
        elif etype == "MULTIPLE_FACES":
            summary["multi_face_count"] += 1
        elif etype == "TAB_BLUR":
            summary["tab_blur_count"] += 1
    return summary


def derive_integrity(
    events: List[Dict[str, Any]],
    accessible_mode: bool = False,
    camera_off: bool = False,
) -> Dict[str, Any]:
    """Compute ``integrity_flag`` / ``auto_blur`` / ``summary`` for a batch of events.

    ``CAMERA_OFF`` (Accessible Mode) takes precedence: the run is recorded as
    ``assisted_unverified`` — unproven rather than clean, and never an error.
    """
    events = events or []
    summary = summarize_events(events)
    camera_off = camera_off or any(e.get("type") == "CAMERA_OFF" for e in events)

    if camera_off or accessible_mode:
        return {
            "integrity_flag": INTEGRITY_ASSISTED_UNVERIFIED,
            "auto_blur": False,
            "summary": summary,
            "accessible_mode": True,
        }

    suspicious = any(
        summary[key] > 0 for key in ("gaze_drift_count", "multi_face_count", "tab_blur_count")
    )
    return {
        "integrity_flag": INTEGRITY_ASSISTED if suspicious else INTEGRITY_CLEAN,
        "auto_blur": suspicious,
        "summary": summary,
        "accessible_mode": False,
    }


def score_adjustment(integrity_flag: Optional[str]) -> int:
    return INTEGRITY_ADJUSTMENT.get((integrity_flag or INTEGRITY_CLEAN).strip(), 0)


def passed(chapter_score: int) -> bool:
    """Single gate rule, one place, so the threshold cannot drift between endpoints."""
    return int(chapter_score) >= UNLOCK_THRESHOLD


if __name__ == "__main__":  # pragma: no cover
    import json

    print(json.dumps(derive_integrity([{"type": "GAZE_DRIFT", "at_ms": 1}]), indent=2))

"""Model client for Assay AI.

Google-only (ADR 001): every call goes through the official ``google-genai`` SDK.

Robustness (DEV3-ROADMAP risk R8): model IDs drift and free tiers change. This client
walks a per-role model fallback chain and rotates across the API keys in ``.env``,
treating 404 as "model retired -> next model", 429/5xx as "try next key, then next
model". When nothing succeeds it returns ``None`` and the caller falls back to a
deterministic fixture (``DEMO_MODE=cached`` or no key behaves the same way).

Never logs or returns key material.
"""
from __future__ import annotations

import json
import os
import re
import threading
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]

_KEY_NAMES = ("GOOGLE_API_KEY", "GOOGLE_API_KEY_FALLBACK", "GOOGLE_API_KEY_FALLBACK_2")

# Fallback chains (first entry is the preferred ID; see ai/MODELS.md).
_DEFAULT_FLASH = ("gemini-3-flash-preview", "gemini-3.8-flash", "gemini-flash-latest", "gemini-3.5-flash")
# Pro free tier is 0 for the current keys, so the chain ends on a flash ID: the
# verifier then runs on Flash instead of Pro (documented in ai/MODELS.md).
_DEFAULT_PRO = ("gemini-3.1-pro-preview", "gemini-pro-latest", "gemini-3-flash-preview")


def _load_dotenv() -> None:
    """Populate os.environ from the repo .env without overwriting real env vars."""
    env = _REPO / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


_load_dotenv()


def _keys() -> list[str]:
    out: list[str] = []
    for name in _KEY_NAMES:
        v = (os.environ.get(name) or "").strip()
        if v and v not in out and "your" not in v.lower():  # skip .env.example placeholder
            out.append(v)
    return out


def demo_mode() -> bool:
    """True when the engine should serve deterministic cached output (no live calls)."""
    return (os.environ.get("DEMO_MODE", "cached") or "").strip().lower() == "cached"


def _chain(env_primary: str, env_fallbacks: str, default: tuple[str, ...]) -> list[str]:
    primary = (os.environ.get(env_primary) or default[0]).strip()
    extra = [m.strip() for m in (os.environ.get(env_fallbacks) or "").split(",") if m.strip()]
    ordered = [primary, *extra, *default]
    seen: list[str] = []
    for m in ordered:
        if m and m not in seen:
            seen.append(m)
    return seen


def models(role: str = "flash") -> list[str]:
    """Ordered model fallback chain for a latency class."""
    if role == "pro":
        return _chain("GEMINI_PRO_MODEL", "GEMINI_PRO_MODEL_FALLBACKS", _DEFAULT_PRO)
    return _chain("GEMINI_MODEL", "GEMINI_MODEL_FALLBACKS", _DEFAULT_FLASH)


def model_id(role: str = "flash") -> str:
    """Preferred (first) model ID for a latency class."""
    return models(role)[0]


_lock = threading.Lock()
_clients: dict[int, object] = {}
_ring = {"i": 0}

_RETRY_HINTS = (
    "429", "resource_exhausted", "quota", "rate limit", "rate_limit",
    "503", "500", "unavailable", "overloaded", "deadline", "timeout",
    "401", "403", "api key", "api_key", "permission", "unauthenticated",
)
_DEAD_MODEL_HINTS = ("404", "not_found", "no longer available", "not found", "unsupported")


def _parse_json(text: str):
    s = (text or "").strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.M).strip()
    try:
        return json.loads(s)
    except Exception:
        return None


def _client_for(i: int, key: str):
    with _lock:
        client = _clients.get(i)
        if client is None:
            from google import genai
            from google.genai import types
            timeout_ms = int(os.environ.get("GEMINI_HTTP_TIMEOUT_MS", "30000"))
            client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=timeout_ms))
            _clients[i] = client
        return client


def generate(prompt: str, *, schema: dict | None = None, role: str = "flash"):
    """Call Gemini across the model chain and key ring.

    Returns a parsed dict when ``schema`` is set, else text. Returns ``None`` when
    offline, unconfigured, or every (model, key) pair fails.
    """
    if demo_mode():
        return None
    keys = _keys()
    if not keys:
        return None

    from google.genai import types

    for model in models(role):
        start = _ring["i"]
        for offset in range(len(keys)):
            i = (start + offset) % len(keys)
            try:
                client = _client_for(i, keys[i])
                config = types.GenerateContentConfig(temperature=0)
                if schema is not None:
                    config = types.GenerateContentConfig(
                        temperature=0,
                        response_mime_type="application/json",
                        response_schema=schema,
                    )
                resp = client.models.generate_content(model=model, contents=prompt, config=config)
                text = getattr(resp, "text", None) or ""
                _ring["i"] = i  # remember the working key
                return _parse_json(text) if schema is not None else text
            except Exception as exc:  # noqa: BLE001 - rotation must swallow per-key errors
                msg = str(exc).lower()
                if any(h in msg for h in _DEAD_MODEL_HINTS):
                    break  # model retired for this project -> next model in the chain
                if any(h in msg for h in _RETRY_HINTS):
                    continue  # transient/quota -> next key, then next model
                return None  # non-retryable (e.g. 400): don't hammer the rest
    return None

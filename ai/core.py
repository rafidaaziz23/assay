"""Pure, deterministic logic for the Assay engine — no network, no I/O.

Everything here is a plain function of its inputs so it is trivially testable and
mockable. LLM-backed behaviour lives in ``ai/__init__.py`` and falls back to these.
"""
from __future__ import annotations

import re

# Fixed seed taxonomy (ADR 004 section 2.1). Served from GET /api/v1/roles.
SEED_ROLES = [
    "Frontend", "Backend", "Fullstack", "DevOps", "Data/ML",
    "Mobile", "QA/Test", "Security", "System Design",
]
OTHERS = "Others"

# Keyword hints per seed role. Deterministic fallback for classify_intent when no
# model is available; the live path is a model classification, not this table.
_ROLE_KEYWORDS = {
    "Frontend": ["react", "vue", "svelte", "css", "html", "dom", "browser", "ui ", "frontend", "hook", "rendering", "tailwind", "component"],
    "Backend": ["api", "server", "rest", "graphql", "endpoint", "database", "sql", "node", "django", "flask", "fastapi", "spring", "query"],
    "Fullstack": ["fullstack", "full-stack", "end-to-end", "end to end", "web app", "browser click", "database row"],
    "DevOps": ["docker", "kubernetes", "k8s", "ci/cd", "cicd", "pipeline", "deploy", "terraform", "aws", "gcp", "cloud", "devops", "container"],
    "Data/ML": ["machine learning", "ml ", "training", "neural", "pytorch", "tensorflow", "pandas", "data pipeline", "llm", "embedding", "recommendation model"],
    "Mobile": ["ios", "android", "swift", "kotlin", "react native", "flutter", "mobile", "offline", "sync", "reconnects"],
    "QA/Test": ["testing", "unit", "integration", "end-to-end", "qa", "coverage", "pytest", "jest", "test strategy", "test"],
    "Security": ["security", "auth", "oauth", "jwt", "encryption", "vulnerability", "xss", "csrf", "penetration", "owasp"],
    "System Design": ["system design", "scalability", "distributed", "architecture", "throughput", "consistency", "sharding", "microservice", "heavy load", "stays consistent"],
}

# Multi-role signals: an intent that names a whole request path or all test layers is
# Fullstack/QA by construction, not whichever role keyword happens to score highest.
_FULLSTACK_SIGNALS = ("browser click", "database row", "request travels", "from the browser", "web app end")
_QA_SIGNALS = ("test strategy", "unit, integration", "unit integration", "test layers", "covering unit", "integration, and end")


def classify_intent(intent: str) -> dict:
    """Deterministic intent -> role classification (ADR 004).

    Returns ``{role_guess, suggested_others, confidence}``. ``suggested_others`` is True
    when no seed role matches, so the UI surfaces the free-text role path.
    """
    text = (intent or "").lower()

    # Whole-path / test-layers intents are unambiguous before keyword scoring.
    if any(s in text for s in _FULLSTACK_SIGNALS):
        return {"role_guess": "Fullstack", "suggested_others": False, "confidence": 0.85}
    if any(s in text for s in _QA_SIGNALS):
        return {"role_guess": "QA/Test", "suggested_others": False, "confidence": 0.85}

    best_role, best_hits = None, 0
    for role, keywords in _ROLE_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits > best_hits:
            best_role, best_hits = role, hits
    if best_role is None:
        return {"role_guess": OTHERS, "suggested_others": True, "confidence": 0.4}
    # Confidence grows with hit count but stays below a hard 1.0.
    confidence = min(0.95, 0.6 + 0.1 * best_hits)
    return {"role_guess": best_role, "suggested_others": False, "confidence": round(confidence, 2)}


def normalize_role(role: str, role_is_custom: bool, custom_role: str) -> str:
    """Resolve the effective role, enforcing the ADR 004 contract.

    ``Others`` requires ``role_is_custom`` and a non-empty ``custom_role``; any unknown
    role is coerced to ``Others`` rather than silently accepted.
    """
    role = (role or "").strip()
    if role == OTHERS or role not in SEED_ROLES:
        custom = (custom_role or "").strip()
        if role_is_custom and custom:
            return custom
        return OTHERS
    return role


# Integrity flag -> chapter-score adjustment. Honeypot and focus are score
# dimensions, not gates (ADR 002 section 2.4). "assisted" is a small penalty;
# "assisted_unverified" (accessible mode, camera off) is neutral.
INTEGRITY_ADJUSTMENT = {"clean": 0, "assisted": -3, "assisted_unverified": 0}


def score_chapter(reasoning_score: int, integrity_score: int, honeypot_points: int,
                  integrity_flag: str = "clean") -> dict:
    """Combine dimensions into the chapter score (ADR 002).

    # ponytail: chapter_score is a gate (>= 75), so reasoning must dominate and the
    # honeypot/focus adjustments stay tiny. One bad honeypot answer cannot fail a
    # chapter on its own. Formula is frozen here, not model-generated (ADR 002 s2.3).
    """
    adjustment = INTEGRITY_ADJUSTMENT.get((integrity_flag or "clean").strip(), 0)
    raw = int(reasoning_score) + int(honeypot_points) + adjustment
    chapter = max(0, min(100, raw))
    return {
        "chapter_score": chapter,
        "reasoning_score": int(reasoning_score),
        "integrity_score": int(integrity_score),
        "honeypot_score": int(honeypot_points),
    }


def calibration_label(predicted: int, actual: int) -> dict:
    """Calibration gap and label (API-CONTRACTS section 2.6)."""
    gap = int(predicted) - int(actual)
    if gap > 15:
        label = "overconfident"
    elif gap < -15:
        label = "underconfident"
    else:
        label = "well_calibrated"
    return {"calibration_gap": gap, "label": label}


def suggest_questions(chapter: dict, selection: str) -> list[str]:
    """Deterministic 3-question fallback for a selected phrase (section 2.4)."""
    topic = (chapter or {}).get("title") or (chapter or {}).get("topic") or "this topic"
    sel = (selection or "").strip() or topic
    return [
        f"What would break if {sel} did not exist?",
        f"How does {sel} trade off against the alternative approach?",
        f"Where does {sel} become the bottleneck?",
    ]


def infer_source_pages(doc_index: dict | None, chapter_title: str, fallback_page: int = 1) -> list[int]:
    """Pick source pages for a chapter from an indexed document (deterministic)."""
    if not doc_index:
        return []
    pages = doc_index.get("pages") or []
    words = [w for w in re.split(r"\W+", (chapter_title or "").lower()) if len(w) > 3]
    hits = []
    for page in pages:
        text = (page.get("text") or "").lower()
        if words and any(w in text for w in words):
            hits.append(int(page.get("page", fallback_page)))
    return sorted(set(hits)) or [fallback_page]

# Assay AI — Model Registry

Single source of truth for model IDs used by the Assay engine. Aligned with
`docs/adrs/001-model-selection.md` (Google-only, two-tier by latency class) and the
DEV3-ROADMAP risk R8 ("model-ID mismatch") — IDs drift, so this file records what
actually works against the current keys.

## Pinned models

| Role | Preferred ID | Env override |
|---|---|---|
| `flash` — latency-sensitive hot path (intake gating, PDF chunking, checklist, honeypot injection, interview follow-up) | `gemini-3.1-flash-lite` | `GEMINI_MODEL` |
| `pro` — off-critical-path depth (final chapter reasoning eval, async verifier pass) | `gemini-3.1-pro-preview` | `GEMINI_PRO_MODEL` |

Each role also has an ordered fallback chain (`GEMINI_MODEL_FALLBACKS` /
`GEMINI_PRO_MODEL_FALLBACKS`). The client walks the chain on a 404 (retired model) and
rotates across the three keys on 429/5xx. See `ai/_client.py`.

## Observed availability (current keys, free tier)

| Model ID | Result | Note |
|---|---|---|
| `gemini-2.5-flash` | 404 | "no longer available to new users" — retired for this project |
| `gemini-2.5-pro` | 404 | retired for this project |
| `gemini-3.1-flash-lite` | 200 | **500 req/day** — the default since 2026-10-18 |
| `gemini-3-flash-preview` | 200 | works, but only **20 req/day** free tier |
| `gemini-3.8-flash` | 503 | valid but high-demand spikes |
| `gemini-flash-latest` | 503 | valid but high-demand spikes |
| `gemini-3.1-pro-preview` | 429 | **free-tier quota = 0** (`generate_content_free_tier_requests: limit 0`) |
| `gemini-pro-latest` | 429 | free-tier quota = 0 |
| `gemini-4-argon` | 429 | free-tier quota = 0 |

**Consequence:** the Pro tier is unusable on the free tier, so `verify_score` falls
back to a Flash model (the pro chain ends on `gemini-3.1-flash-lite`). This is a
second-model cross-check, not a Pro-depth check; record it as a known limitation if a
judge asks why the verifier runs on Flash.

**Why the default is Lite, not Flash (2026-10-18):** measured daily free-tier limits
on this key's project are `gemini-3-flash-preview` = 20 req/day and
`gemini-3.1-flash-lite` = 500 req/day. 20/day is a single demo run — a judge opening
the app twice exhausts it, and the per-request fallback then serves fixtures, which
reads as broken rather than degraded. Lite answers Socratic counter-questions
correctly (verified against a gradient-descent prompt, ~2.1 s), so it is the default
until a paid tier is in play.

## Rules

- **Google-only.** Every call goes through the official `google-genai` SDK. No other
  provider appears in `ai/` or `backend/` (ADR 001 §2.3 — cup hard rule; a non-Google
  model in the dependency tree risks zero-scoring under Technical Merit).
- **Env override.** `.env` sets `GEMINI_MODEL` / `GEMINI_PRO_MODEL` (+ `_FALLBACKS`);
  the code reads those names, never hard-codes a model string at a call site.
- **Per-call timeout.** `GEMINI_HTTP_TIMEOUT_MS` (default 30000) bounds every request so
  a hung socket cannot wedge a call site.
- **Structured output.** Both tiers support strict `response_schema`; valid JSON
  measured 4/4 in `reza-research/parts10/HASIL-TES-EMPIRIS.md` (P5), and re-verified
  live by `eval/smoke_structured.py`.
- **Do not silently re-point.** Changing a preferred ID moves the latency/cost profile;
  note it here and in the log.

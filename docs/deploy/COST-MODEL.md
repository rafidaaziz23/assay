# Assay — Cost Model (Cloud Run, `asia-southeast1`)

> **Verified:** 17 Oct 2026. Every rate below was pulled from the **Cloud Billing
> Catalog API** (`cloudbilling.googleapis.com/v1/services/.../skus`) filtered to
> `serviceRegions = asia-southeast1`, not from blog posts. Rates carry
> `effectiveTime: 2026-10-17T07:00:00Z`.
>
> Re-verify any time with `tools/cost-probe.sh`.

---

## TL;DR — what you actually pay

| Scenario | Monthly gross | Monthly billed |
|---|---|---|
| **Demo / judging** (`min-instances=0`) | **$0.11** | **$0.00** |
| Always-on (`min-instances=1`, both services) | $17.60 | **$12.38** |
| Artifact Registry (1 image pair) | $0.00 | **$0.00** |
| Cloud Build (10 builds/mo) | $0.00 | **$0.00** |
| Gemini tokens (100 demo sessions) | ~$1.70 | see §7 |

**Billed = $0.00 at demo load.** The only way to get a real charge here is
`min-instances=1`, which is a config choice, not a usage effect.

---

## 1. Cloud Run rates — Singapore is **Tier 2**

This is the single most-missed detail. Google publishes `$0.000024 / vCPU-s`
everywhere, but that is **Tier 1** (`us-central1`, Tokyo, Taiwan). Singapore is
**Tier 2** and costs **40% more**.

Verbatim from `cloud.google.com/run/pricing`:

> Subject to **Tier 2** pricing
> asia-east2 (Hong Kong) … **asia-southeast1 (Singapore)** …

Measured SKUs:

| SKU (asia-southeast1) | Rate |
|---|---|
| `Services CPU Tier 2 (Request-based billing)` | `$0.0000336` / vCPU-second |
| `Services Memory Tier 2 (Request-based billing)` | `$0.0000035` / GiB-second |
| `Services Min Instance CPU Tier 2 (Request-based billing)` | `$0.0000035` / vCPU-second |
| `Services Min Instance Memory Tier 2 (Request-based billing)` | `$0.0000035` / GiB-second |
| `Requests` | `$0.0000004` each (= `$0.40` / million) |

> **Note the inversion:** an *idle* min-instance vCPU (`$0.0000035`) costs about
> **10× less** than an *active* one (`$0.0000336`). Keeping one instance warm is
> cheap per second but runs 2,628,000 seconds a month, so it still adds up.

---

## 2. Free tier — and the Tier 2 trap

Monthly, per **billing account** (aggregated across projects), resets monthly:

| Resource | Free allowance |
|---|---|
| CPU | 180,000 vCPU-seconds |
| Memory | 360,000 GiB-seconds |
| Requests | 2,000,000 |

**Trap:** verbatim from the pricing page —

> "The free tier is applied as a **spending based discount using Tier 1 pricing**."

So the free tier is not 180,000 vCPU-seconds in Singapore. It is a **$5.22
discount** (180,000 × $0.000024 + 360,000 × $0.0000025). At Tier 2 rates that
discount buys only **155,357 vCPU-seconds**, not 180,000.

Budget the discount as money, not as seconds.

---

## 3. Component-by-component at demo load

Deployed shape: **2 services**, `1 vCPU / 512 MiB` each, `min-instances=0`,
`max-instances=2`, request-based billing.

### 3a. `assay-api` (FastAPI + `ai/` engine + `prompts/`)

Image: **282 MB**. Measured cold start: **8,351 ms** (Docker local, warm disk —
Cloud Run will be slower on a true cold node).

Demo traffic assumption: 100 sessions × 30 s of billed CPU time.

| Line | Calculation | Gross |
|---|---|---|
| CPU | 3,000 s × $0.0000336 | $0.1008 |
| Memory | 3,000 s × 0.5 GiB × $0.0000035 | $0.0053 |
| Requests | 1,000 × $0.0000004 | $0.0004 |
| **Subtotal** | | **$0.1065** |
| Free-tier discount | | −$5.22 |
| **Billed** | | **$0.00** |

Cold starts: 100 × 8.351 s = 835 vCPU-s = **$0.028** gross. Already inside the
discount.

### 3b. `assay-web` (nginx + React `dist`)

Image: **50.1 MB**. Static files, ~50 ms billed CPU per request.

Demo traffic: 5,000 requests (one SPA load + assets each, cached after first).

| Line | Calculation | Gross |
|---|---|---|
| CPU | 250 s × $0.0000336 | $0.0084 |
| Memory | 250 s × 0.5 GiB × $0.0000035 | $0.0004 |
| Requests | 5,000 × $0.0000004 | $0.0020 |
| **Subtotal** | | **$0.0108** |
| **Billed** | | **$0.00** |

### 3c. AI engine (`ai/` + `prompts/`)

**$0.00 as infrastructure.** It is a Python package imported directly by
`backend/app/services/engine.py`; it is not a third service. It ships inside the
`assay-api` image (already counted in 282 MB). Its cost appears only as Gemini
tokens — see §7.

### 3d. Combined

| Component | Gross | Billed |
|---|---|---|
| `assay-api` compute | $0.1065 | $0.00 |
| `assay-web` compute | $0.0108 | $0.00 |
| AI engine | $0.0000 | $0.00 |
| **Total** | **$0.1173** | **$0.00** |

---

## 4. Always-on (`min-instances=1`) — the real bill

Only if you need zero cold starts. 730 h/month = 2,628,000 s.

Per service (`1 vCPU`, `0.5 GiB`, idle rates):

| Line | Calculation | Gross |
|---|---|---|
| Idle CPU | 2,628,000 × $0.0000035 | $9.198 |
| Idle memory | 2,628,000 × 0.5 × $0.0000035 | $4.599 |
| **Per service** | | **$13.797** |

Both services: **$27.59** gross → minus $5.22 free tier → **$22.37/month**.

> **Recommendation: do not use `min-instances=1`.** Beyond the money, your
> session store is `InMemoryStore` (`backend/app/repositories/`), so a warm
> instance does **not** preserve sessions across *different* instances anyway.
> `max-instances=2` means a session can still land on the other instance.

---

## 5. Artifact Registry

`Artifact Registry Storage` (global): first **0.5 GiB free**, then **$0.10 / GiB-month**.

| State | Size | Billed |
|---|---|---|
| One pair of images | 282 MB + 50 MB = 0.324 GiB | **$0.00** (inside 0.5 GiB) |
| Two versions kept | 0.648 GiB | **$0.015 / month** |
| Ten versions kept | 3.24 GiB | **$0.274 / month** |

Headroom is **0.176 GiB** — a single extra backend push crosses the line. Prune
after every deploy (the deploy script does).

---

## 6. Cloud Build

| Line | Rate |
|---|---|
| Free tier | 2,500 build-minutes / month |
| Beyond free tier (`e2-standard-2`) | `$0.006` / minute |

Two builds ≈ 10 min. **$0.00.** You would need ~250 deploys a month to pay.

---

## 7. Gemini tokens

> **Status: UNMEASURED.** I could not measure real token counts — see §9. The
> figures below are `ASUMSI` built from published SKU rates only.

Rates (verified SKUs, per token):

| Model | Input | Output |
|---|---|---|
| `gemini-3-flash` (text) | `$0.0000005` = **$0.50 / 1M** | `$0.000003` = **$3.00 / 1M** |
| `gemini-3.8-flash` (text) | `$0.00000075` = **$0.75 / 1M** | `$0.00000375` = **$3.75 / 1M** |

`ASUMSI:` one checklist call ≈ 2,000 input + 800 output tokens.
`ASUMSI:` one demo session ≈ 5 model calls.

At `gemini-3-flash` rates:

| Line | Calculation | Cost |
|---|---|---|
| Input | 2,000 × $0.0000005 | $0.0010 |
| Output | 800 × $0.000003 | $0.0024 |
| Per call | | $0.0034 |
| 100 sessions × 5 calls | 500 × $0.0034 | **$1.70** |

**This is the largest real cost in the whole deployment**, and it is entirely
absorbed by the $300 credit. It is also the number most likely to be wrong —
measure it once the model ID is fixed (§9).

---

## 8. Egress

Cloud Run internet egress uses Premium tier. Free allowance is **1 GiB/month
within North America only** — Singapore egress is **$0.12 / GiB**.

A demo serving 5,000 requests of ~200 KB gzipped assets ≈ 1 GiB ≈ **$0.12**.
Cached assets make repeat loads free. Not a concern at demo scale.

---

## 9. What I could NOT verify (read this)

1. **`gemini-2.5-flash` returns `404 NOT_FOUND`.** Verbatim from the API:
   > "This model models/gemini-2.5-flash is no longer available to new users.
   > Please update your code to use models/gemini-3.8-flash"

   `backend/app/config.py:17` still defaults to `gemini-2.5-flash`. The repo
   `.env` overrides it to `gemini-3-flash-preview`, so local runs use the live
   path — but **the container gets no `.env`** (`.dockerignore` excludes it).
   Unless `GEMINI_MODEL` is injected at deploy time, production falls back to the
   dead ID and silently serves deterministic fixtures.

2. **Quota is exhausted right now.** Verbatim:
   > "Quota exceeded for metric: generate_content_free_tier_requests,
   > limit: 20, model: gemini-3.8-flash … Please retry in 10h11m"

   Free tier = **20 requests/day** on this key. That is far below what a live
   demo needs. Linking billing raises the limit (Tier 1) but also starts billing
   tokens at §7 rates.

3. **Token counts unmeasured** because of (1) and (2). Re-run
   `tools/cost-probe.sh` after the model ID is fixed.

4. **Prepayment split unverified.** Whether the IDR 500,000 lands as a separate
   Postpay balance or merges into the $300 promo credit cannot be checked until
   the account is open (`gcloud` exposes no prepayment balance command).

---

## 10. Sources

| Claim | Source |
|---|---|
| All Cloud Run rates | `cloudbilling.googleapis.com/v1/services/152E-C115-5142/skus` |
| All Artifact Registry rates | `cloudbilling.googleapis.com/v1/services/149C-F9EC-3994/skus` |
| All Cloud Build rates | `cloudbilling.googleapis.com/v1/services/8B5D-EF7D-EB12/skus` |
| All Gemini rates | `cloudbilling.googleapis.com/v1/services/AEFD-7695-64FA/skus` |
| Tier 1 / Tier 2 region split | `cloud.google.com/run/pricing` |
| Free tier discount mechanism | `cloud.google.com/run/pricing` |
| 20 req/day free quota | Live API error response |
| Model retirement | Live API error response |

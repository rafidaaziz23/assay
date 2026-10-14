# DEV3 OVERNIGHT BRIEF — Assay (AI Engine & Eval)

Kontrak kerja buat run semalaman tanpa manusia. Dibaca **di awal tiap run**, bukan sekali.
Kalau brief ini dan ingatan/tebakanmu berbeda, **brief ini yang benar**.

- **Repo:** `D:/Project/assay` (ini repo produk; yang di `ai-builder-cup-research` cuma spek)
- **Sumber rencana:** `D:/Project/ai-builder-cup-research/active-learning-engine/DEV3-ROADMAP.md`
- **Otoritas dokumen:** `DEV3-ROADMAP.md` §1 → `docs/API-CONTRACTS.md` (LOCKED) → `docs/PRD.md`
  → ADR `docs/adrs/001..005`. Kalau bertabrakan: **API-CONTRACTS menang**.
- **Gate:** `tools\gate-dev3.cmd` (wajib; exit 0 = hijau)
- **Jejak:** `docs/DEV3-OVERNIGHT-LOG.md` — satu entri per unit, ditulis SEBELUM lanjut
- **Mulai:** 2026-10-14 malam

## 0a. Mode kerja & keputusan run (dari Reza)

- **Ini `/goal` loop.** Tiap akhir turn, judge ngecek goal. Kalau belum kelar, lu auto-lanjut.
  **Jangan berhenti dan nanya** — kerjakan unit berikutnya sampai habis budget atau goal `done`.
- **Scope malam ini:** Hari 0–2 (H0.x, H1.x, H2.x). Hari 3 (H3.x) **hanya kalau** semua H0–H2
  `DONE` dan masih ada waktu. Jangan mulai H3 sebelum H0–H2 beres.
- **Commit lokal, jangan push.** Pesan commit + komentar kode **wajib bahasa Inggris** (commit
  `feat(ai): ...`; komentar kode English). Isi log/brief boleh Indonesia.
- **API key = HEMAT.** Live call cuma buat 1–2 bukti per unit (yang emang butuh model). Sisanya
  offline/cached. Tiga key di `.env`, urutan rotasi: `GOOGLE_API_KEY` → `GOOGLE_API_KEY_FALLBACK`
  → `GOOGLE_API_KEY_FALLBACK_2`. Kalau satu key balik `429`/`RESOURCE_EXHAUSTED`, langsung pakai
  key berikutnya; kalau ketiganya habis, tandai unit yang butuh live sebagai `BLOCKED (quota)` dan
  lanjut unit offline.
- **Jaring pengaman:** cron `assay-dev3-watchdog` kirim ringkasan log ke Telegram tiap 15 menit
  kalau ada perubahan. Kalau lu lihat pesan STUCK, tulis di log dan coba lanjut.

---

## 0. Aturan keras (pelanggaran = run gagal)

1. **HANYA tulis di:** `ai/`, `prompts/`, `eval/`, `tools/gate-dev3.cmd`, `docs/DEV3-*.md`,
   `ai/MODELS.md`, `ai/FIXTURES.md`. **JANGAN sentuh** `frontend/`, `backend/`, `docs/*` lain,
   `.gitignore`, `package.json`, `README.md`. Itu milik DEV 1 / DEV 2.
2. **Google-only di runtime produk.** Cuma `google-genai` SDK. Nol provider lain di `ai/` atau `backend/`.
3. **Nol rahasia di file yang bisa ke-commit.** API key ada di `D:/Project/assay/.env` (gitignored).
   Baca dari situ; jangan cetak nilainya; jangan tulis ke brief/log/commit. Nol chat id / token di repo.
4. **Nol angka karangan.** Angka apa pun cuma boleh dari `eval/results/` atau
   `ai-builder-cup-research/reza-research/parts10/HASIL-TES-EMPIRIS.md`. Dilarang bikin angka baru.
5. **Commit lokal per unit, JANGAN push.** Remote itu repo tim. `git add <file unit>` saja,
   conventional message (`feat(ai): ...` / `test(eval): ...`). Jangan `git add -A` buta, jangan `--force`.
6. **Jangan pernah nanya manusia, jangan nunggu approval.** Kalau kepepet: catat blocker di log,
   tandai unit `BLOCKED`, lanjut unit berikutnya yang masih bisa dikerjakan.
7. **Pure function.** Semua di `ai/` tanpa I/O jaringan kecuali panggilan model. Gampang dites.
8. **Gate hijau itu syarat**, bukan bonus. Unit baru boleh ditandai `DONE` setelah gate hijau.

## 1. Setup tiap run (5 detik)

```bash
cd /d/Project/assay
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || echo "VENV BELUM ADA — lihat unit H0.1"
```

Kalau `.venv` belum ada: kerjakan **H0.1** dulu (bikin venv + install), itu prasyarat semua unit.

## 2. Cara milih unit

1. Baca `docs/DEV3-OVERNIGHT-LOG.md` — cari unit pertama yang **belum** `DONE`.
2. Kerjakan **SATU unit** itu sampai kelar + gate hijau. Jangan kerjakan dua unit sekaligus.
3. Kalau unit besar (mis. H0.3), boleh selesai di run ini saja; jangan pindah sebelum `DONE`.
4. Tulis entri log (format §5), commit lokal, lalu **akhiri run** dengan status 3 baris (§6).

## 3. Daftar unit (urut; kerjakan dari atas)

Tiap unit punya **aksi**, **artefak**, **"DONE kalau"** (verifikasi konkret). Ambil dari
`DEV3-ROADMAP.md` §2–§5; ringkasannya di bawah supaya run nggak perlu baca ulang tiap kali
(baca roadmap kalau butuh detail).

### HARI 0 — setup & baseline
| ID | Aksi | DONE kalau |
|---|---|---|
| H0.1 | `.venv` (python 3.11/3.12) + install `google-genai pytest pytest-asyncio python-dotenv pymupdf reportlab pypdf`. Tulis `ai/MODELS.md` (ID model persis + samakan ADR 001). | `.venv/Scripts/python.exe -c "import google.genai, fitz, pytest"` sukses; `ai/MODELS.md` ada |
| H0.2 | `eval/smoke_structured.py`: panggil Flash pakai `response_schema` dari API-CONTRACTS §4, parse JSON. Mode `--offline` = validasi schema lokal (nol jaringan). | `python eval/smoke_structured.py` cetak `JSON OK` tanpa exception |
| H0.3 | Stub SEMUA fungsi `DEV3-ROADMAP §1` di `ai/__init__.py` (balikin fixture statis shape API-CONTRACTS) + `ai/FIXTURES.md` (contoh output tiap fungsi). | `python -c "import ai; ai.classify_intent('x')"` balik dict ber-shape; FIXTURES.md ada |
| H0.4 | `eval/classify.py`: port logika regex dari `reza-research/parts10/honeypot_test.py` (REFUSE/HEDGE/HALLUCINATE/ERROR). **Jangan ubah definisi label** (biar bisa dibanding baseline n=80). | fungsi `classify(text)` ada; unit test kecil hijau |
| H0.5 | `prompts/honeypot-catalog.json`: 10 term fiktif dipetakan ke topik (ADR 005). Term boleh ambil dari `honeypot_test.py` TERMS + yang sudah ada di `backend/app/services/honeypot_catalog.py` (jangan ubah file backend itu). | file JSON valid, 10 entri, tiap entri ada `term`+`category`+`trap_type`+`expected_action` |

### HARI 1 — intake → checklist → syllabus
| ID | Aksi | DONE kalau |
|---|---|---|
| H1.1 | `ai.classify_intent` (ADR 004): intent → `role_guess` dari 9 seed + `suggested_others`. | 10 intent uji (5 seed, 5 aneh) → `suggested_others` bener ≥ 9/10; tulis `eval/results/intent_cases.jsonl` |
| H1.2 | `ai.gen_checklist`: item + `origin` (`document`/`role_taxonomy`/`grounded_external`) + `confidence`. | 1 intent + 1 PDF → ≥ 3 item, tiap item `origin` valid |
| H1.3 | `ai.index_document`: ekstraksi teks + **nomor halaman** (page-anchored, PyMuPDF). | PDF contoh → tiap chunk punya `page`; total halaman cocok PDF asli |
| H1.4 | `ai.synth_syllabus`: chapter `title/order/objectives/estimated_reading_minutes/source_pages`. Jalur tanpa PDF → `source_mode: role_taxonomy_generated`. | 2 run (dengan & tanpa PDF) → ≥ 3 chapter, `source_pages` ada di jalur PDF, `source_mode` bener |
| H1.5 | Grounding eksternal Google Search untuk **1 chapter saja**, hasil `cached: true`. | `references[]` punya 1 `grounded_external` `cached: true`; matikan jaringan → fallback cache, nol exception |

### HARI 2 — reader ask + interview + honeypot
| ID | Aksi | DONE kalau |
|---|---|---|
| H2.1 | `ai.socratic_ask`: balik nanya/hint, **tidak** jawab langsung. | 10 pertanyaan uji → `gave_direct_answer == False` di 10/10 |
| H2.2 | `ai.suggest_questions`: seleksi multi-kata → 3 pertanyaan relevan, nggak duplikat. | seleksi "reconciliation and diffing" → 3 pertanyaan unik |
| H2.3 | Interview prompt multi-turn (2–3 ronde, HOTS + follow-up adaptif), simpan riwayat, `running_score` naik. | `start_interview`/`interview_turn` balik shape §2.5 |
| H2.4 | `ai.pick_honeypot_term` (lookup katalog + variasi ADR 005, rotasi per sesi) + `ai.classify_honeypot` (4 kelas → poin tetap). | Kasus A copas → `AI_HALLUCINATION_COPYPASTE` −2; Kasus B nolak → `CRITICAL_REJECTION` +2; Kasus C "gak tau" → `UNVERIFIED_HONEST` 0 |
| H2.5 | `ai.score_chapter`: `clamp(reasoning_score + honeypot_points + integrity_adjustment, 0, 100)`; `integrity_adjustment = {clean:0, assisted:-3, assisted_unverified:0}`. Tulis keputusan ini sebagai komentar `# ponytail:` di kode. | tabel kasus (80/−2/assisted) → hasil sesuai rumus |
| H2.6 | `ai.verify_score`: model kedua (Pro) → `status: agreed|uncertain` + note. | 5 skor uji → semua balik `status` valid, nol exception |

### HARI 3 — stretch (kalau H0–H2 semua DONE dan masih ada waktu)
| ID | Aksi | DONE kalau |
|---|---|---|
| H3.1 | `ai.calibration_label`: `overconfident` (pred > actual+15), `underconfident` (pred < actual−15), `well_calibrated`. | 3 kasus batas (gap 20/−20/5) label bener |
| H3.2 | Appeal handler stub: `{appeal_id, status:"under_review", reviewer:"verifier_model", possible_outcome:[...]}`. | balik shape §2.8 |
| H3.3 | `eval/harness.py` (caller threaded workers=5) + `run_honeypot.py`, `run_traps.py`, `run_verifier.py`, `run_structured.py` + `eval/report.py` → tabel markdown. Jalan **atas model Google produk** (Flash/Pro). | `python eval/report.py` → tabel keluar, tiap baris ada `n`, nol angka tanpa `n` |
| H3.4 | Kunci angka: bandingkan produk vs baseline riset, catat kenapa kalau beda. Kasih tabel final di log. | tabel final ada di `eval/results/` + log |

## 4. Gate

```cmd
tools\gate-dev3.cmd
```
Hijau = exit 0. Isinya (offline, < 300s): `import ai` + `pytest eval/tests -q` (kalau ada)
+ validasi `prompts/honeypot-catalog.json`. Kalau merah: baca output, perbaiki, ulang.
**Maks 3 percobaan per unit.** Kalau masih merah → tandai unit `BLOCKED`, tulis apa adanya di log, lanjut.

Gate ini **offline** — dia nggak nguji panggilan model. Kalau unit butuh bukti live (grounding, verdict),
jalankan skrip verifikasinya manual dan **tempel hasil mentahnya di log**. Jangan klaim "live OK" tanpa output.

## 5. Format entri log (append ke `docs/DEV3-OVERNIGHT-LOG.md`)

```
### <ID> — <judul> — <DONE|BLOCKED|PARTIAL> — <YYYY-MM-DD HH:MM WIB>
- Aksi: <1-2 baris>
- Artefak: <file yang dibuat/diubah>
- Bukti: <perintah + hasil mentah singkat (gate output / verifikasi live)>
- Catatan: <keputusan, konflik kontrak, risiko>
```

## 6. Status akhir run (WAJIB, jadi isi pesan Telegram)

Akhiri tiap run dengan TEPAT 3 baris, singkat:

```
[DEV3] unit=<ID> status=<DONE|BLOCKED|PARTIAL> gate=<HIJAU|MERAH>
sisa: <n unit belum DONE> — berikutnya <ID>
<1 baris kalau ada blocker/keputusan penting, kalau tidak tulis "oke">
```

## 7. Kapan berhenti (stop condition)

- **H0–H2 hijau ≠ selesai.** Jangan berhenti setelah H0–H2. Lanjut ke H3 (H3.1–H3.4) selama budget masih ada.
- **Bounded.** Berhenti buka unit baru jam **07:00 WIB**. Kalau jam segitu belum lewat dan masih ada unit: lanjut.
- Kalau semua unit H0–H3 `DONE` → tulis closing summary di log, lalu **pause job-nya sendiri**:
  ```bash
  hermes cron list            # cari id job 'assay-dev3'
  hermes cron pause <id>
  ```
  dan akhiri run dengan `[DEV3] SELESAI — semua unit DONE`.
- Kalau unit `BLOCKED` dan nggak ada unit lain yang bisa dikerjakan → tulis closing summary + pause job.
- Kalau gate merah 3× di unit yang sama → `BLOCKED`, lanjut unit lain (jangan berhenti total).

## 8. Yang TIDAK dijamin / di luar scope

- `frontend/` dan `backend/` (DEV 1 / DEV 2). Kalau butuh endpoint baru → catat di log, jangan bikin.
- Push ke remote (repo tim). Commit lokal saja.
- Video/deck/pitch. Itu DEV 1.
- Angka baru di luar `eval/results/` dan `HASIL-TES-EMPIRIS.md`.

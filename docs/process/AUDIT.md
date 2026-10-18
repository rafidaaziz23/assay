# AUDIT.md — Critical Assessment & Winning Strategy (v2.0.0)
## Assay: The Active Socratic Learning Engine

**Auditor:** AI Strategic Advisor (Brutally Honest Mode)
**Date:** 14 Oktober 2026 — revisi kedua dari audit 13 Oktober
**Deadline:** 18 Oktober 2026, 23:59 UTC+8 — **HARD DEADLINE** (4 hari kerja tersisa)
**Kontrak yang diaudit:** `PRD.md` v2.0.0 + `API-CONTRACTS.md` v2.0.0 (status: OPERATIONAL CONTRACT, freeze 14 Okt)
**Status:** PRE-BUILD AUDIT — kontrak sudah beku, **belum ada kode produk**.

### Changelog audit ini (v1 → v2)

| Area | v1 (13 Okt) | v2 (14 Okt) |
|---|---|---|
| Nama produk | CogniForge | **Assay** |
| Deadline | "18 Okt, bukan 19" (temuan) | 18 Okt dikonfirmasi di PRD v2 §header — **RESOLVED** |
| Track | "Track 4 DAN 5, pilih satu" | Track 4 saja di PRD v2 — **RESOLVED** |
| Scope | "18 sub-fitur, scope 5 minggu" | Cut list PRD v2 §8 ada — **PARTIAL**, lihat §1 |
| Anti-cheat | "security theater, jangan dijual" | ADR 003: on-device ML + auto-blur + Accessible Mode — **RESOLVED** |
| Honeypot | "belum divalidasi, asumsi" | Sudah diuji empiris (n=80, 4 model) — **PARTIAL**, lihat §12 |
| Fallback | "tidak ada, wajib ada" | `DEMO_MODE=cached` + auto-trigger 429/500/503 — **RESOLVED** |
| Angka | — | Semua angka di dokumen ini bisa ditelusuri ke `../reza-research/parts10/HASIL-TES-EMPIRIS.md`. Tidak ada angka karangan. |

> Catatan link: semua referensi di dokumen ini pakai path relatif dari `active-learning-engine/`. Link `file:///D:/Lab/nexatriv/...` di audit v1 sudah mati dan sudah dibuang.

---

## ⚠️ PREAMBLE: REALITY CHECK

Hari ini **14 Oktober**. Deadline **18 Oktober 2026, 23:59 UTC+8** (timeline panitia: `../01-event-guidelines/02-timeline-schedule.md` — `>>> DEADLINE SUBMISI: 18 OKTOBER 2026 <<<`). Sisa **4 hari kalender**, dan PRD sendiri menargetkan submit di Hari 4 sebelum 20:00.

Empat deliverable wajib:
1. Live Prototype (Cloud Run / Firebase)
2. Video Demo ≤ 3 menit
3. Pitch Deck PDF (10-12 slide)
4. Repositori GitHub publik yang rapi

Yang sudah ada: PRD v2, API-CONTRACTS v2 (LOCKED), ADR 001-005, DEMO-SCRIPT, PITCH-DECK-OUTLINE, COMPETITIVE-ANALYSIS, angka empiris. **Yang belum ada: kode, eval harness yang jalan, deploy, video, deck final.** Itu fakta pertama yang harus dihadapi, dan itu tetap tidak berubah dari audit v1.

---

## 1. STATUS TEMUAN AUDIT v1 — RESOLVED / PARTIAL / OPEN

Ini inti revisi ini: setiap temuan lama diberi status dan bukti, bukan dibiarkan menggantung.

| # | Temuan lama | Status | Bukti / catatan |
|---|---|---|---|
| 1.1 | PRD menulis deadline 19 Okt (salah) | ✅ **RESOLVED** | PRD v2 header: `18 Oktober 2026, 23:59 UTC+8 — HARD DEADLINE`. Jadwal §6 v2 juga berakhir 18 Okt. |
| 1.2 | Scope inflation: 5 pilar / ~18 sub-fitur / scope 5 minggu | ⚠️ **PARTIAL** | PRD v2 §8 punya cut list eksplisit (Monaco+Piston+TDL, DAG visual, dual-metric, voice/Gemini Live, auth, multi-source). Tapi §5 v2 sendiri menghitung **~14.75 dev-day vs kapasitas ~9.6 dev-day**. Cut-nya menyelesaikan *definisi* scope, belum menyelesaikan *aritmatika*-nya. Lihat N1 di §9. |
| 1.3 | Alignment Track 4 DAN Track 5 (ambigu, 1 tim = 1 track) | ✅ **RESOLVED** | PRD v2: `Track Alignment: Track 4 … single track`. COMPETITIVE-ANALYSIS v2 baris 7 sama. |
| 1.4 | PRD inward-looking: target user kabur, tidak ada angka, JAPAC tidak disentuh | ⚠️ **PARTIAL** | PRD v2 §2.3 menambah persona (B2C demo: pelajar/dev per role; B2B story: bootcamp & corporate L&D) + JAPAC (gap 9 juta talenta digital, World Bank; bootcamp completion <15%). **Masih OPEN:** tidak ada TAM/SAM/SOM, tidak ada klaim retensi/ROI yang bisa dipertahankan. Ada `../market-sizing-guide/` di repo tapi belum dipakai PRD. |
| W1 | Scope kebesaran untuk waktu build | ⚠️ **PARTIAL** | Sama dengan 1.2. Lihat N1. |
| W2 | Anti-cheat browser-side = security theater | ✅ **RESOLVED** | ADR 003 menolak CSS-only anti-cheat secara eksplisit; diganti Focus Mode on-device + framing "integrity signal". PRD §7 tidak lagi memakai kata "anti-cheat" sebagai klaim. |
| W3 | Honeypot belum divalidasi empiris — asumsi | ⚠️ **PARTIAL (naik dari OPEN)** | Sudah diukur: **54% halusinasi (n=80, 4 model)**; per model gemini-flash-medium **75%**, deepseek-v4-pro 70%, deepseek-v4-flash 45%, deepseek-v4.1-flash 25%. Klaim "LLM luar bakal halusinasi" **terbukti arahnya, bukan 100%**. 29/80 panggilan REFUSE, 5 HEDGE, 3 ERROR. Residual risk nyata → wajib pin model di demo (§7.2, N4). |
| W4 | LLM menilai LLM = subjektif, tidak ada guardrail deterministik | ⚠️ **PARTIAL** | ADR 002 (deterministic classification dari structured output) + verifier loop (**13/20 halusinasi tertangkap, 65%**) + appeal path + field `confidence`. Tapi verifier **meleset 35%** — jangan klaim "verified", klaim "second-pass check". |
| W5 | Tidak ada fallback mode | ✅ **RESOLVED** | API-CONTRACTS §3: trigger `DEMO_MODE=cached` ATAU header `x-demo-mode: cached` ATAU error Gemini 429/500/503; 2 skenario wajib (success flow + caught flow). |
| W6 | Bahasa submisi harus Inggris, PRD Bahasa Indonesia | ⚠️ **PARTIAL** | PRD v2 §7 menyatakan UI/README/deck/video = Inggris, dokumen internal = Indonesia. Aturannya beres; **artefak Inggrisnya belum ada satu pun**. Effort copywriting ini belum masuk budget Hari 4. Lihat N11. |
| 5.1 | Belum ada ADR / arsitektur formal | ⚠️ **PARTIAL** | ADR 001-005 sudah ada di `docs/adrs/` (model selection, deterministic guardrails, client-side ML, role taxonomy, honeypot catalog). **Masih OPEN:** tidak ada diagram arsitektur (C4/container) di repo — juri rubrik "Ketepatan Arsitektur Sistem" akan mencari ini. |
| 9.3 | Monaco + Piston + TDL = scope project tersendiri | ✅ **RESOLVED** | PRD v2 §8: cut ke roadmap. API-CONTRACTS v2 §0 menghapus state `DEBUG_CHALLENGE`. |
| 9.4 | Anti-cheat browser-side dijual sebagai keamanan | ✅ **RESOLVED** | ADR 003 + PRD §4.5. |
| 9.5 | 4 dev tanpa kontrak API | ✅ **RESOLVED** | `API-CONTRACTS.md` v2 LOCKED (14 Okt), 8 grup endpoint + state machine + JSON schema. Tim jadi 3 dev (PRD §5). |
| 9.6 | Timeline mulai 14 Okt tapi dokumen ditulis 13 Okt malam | ✅ **RESOLVED** | Hari 0 = 14 Okt dipakai untuk kontrak + angka honeypot — dan **memang sudah selesai hari ini**. |
| 9.7 | Honeypot `trigger_round: 2` hardcoded → tidak pernah kena kalau interview cuma 1 ronde | ❌ **MASIH OPEN** | API-CONTRACTS v2 §2.5 contoh masih menaruh honeypot di `turn_index: 2`. Kalau user (atau demo) `finalize` setelah 1 ronde, honeypot tidak ter-inject. Fix: paksa minimum 2 ronde sebelum `finalize`, atau inject di ronde 1 kalau interview diperkirakan pendek. |
| 9.8 | Tidak ada Q&A defense script | ✅ **RESOLVED** | §10 dokumen ini, sudah diperbarui untuk v2. |

**Skor jujur: 8 RESOLVED, 8 PARTIAL, 1 OPEN.** Tim bergerak cepat dan arah perbaikannya benar. Tapi "PARTIAL" yang tersisa semuanya menumpuk di tempat yang sama: **kapasitas 4 hari**.

---

## 2. SWOT ANALYSIS (HONEST) — diperbarui

### 2.1 STRENGTHS

| # | Strength | Justifikasi |
|---|----------|-------------|
| S1 | **Narasi "Anti-AI-Brain-Rot" masih zeitgeist** | 95% mahasiswa pakai AI (HEPI 2026); 67% murid bilang AI merusak cara berpikir mereka (RAND, Mar 2026); PISA 2025 terendah sepanjang sejarah. Juri Google Cloud sadar produk mereka sendiri (NotebookLM) dianggap bagian dari masalah. Mengangkat ini = keberanian + awareness. |
| S2 | **Honeypot kini punya angka, bukan opini** | 54% halusinasi (n=80, 4 model). Tidak ada satu pun platform belajar yang menyuntik konsep fiktif untuk mendeteksi outsourcing pemikiran. Novel, demo-friendly, dan **terukur**. |
| S3 | **AI sebagai "Enforcer", bukan "Assistant"** | 99% project hackathon bikin AI helper. Membalik peran jadi adversarial tutor memisahkan Assay dari ratusan pesaing. |
| S4 | **Alignment kuat ke Track 4** | Track 4 = Media, Content & Digital Experiences, sub-tema adaptive learning untuk retensi. Ini praktis ditulis untuk Assay. |
| S5 | **Kontrak & ADR sudah beku di Hari 0** | Ini yang biasanya bikin tim hackathon mati di Hari 2. Sudah selesai. |

### 2.2 WEAKNESSES

| # | Weakness | Dampak & Realitas |
|---|----------|-------------------|
| W1 | **Aritmatika kapasitas masih defisit ~5 dev-day** | PRD v2 §5: 14.75 dev-day vs ~9.6 efektif. Cut list §8 membuang roadmap item, bukan item yang sudah dihitung. Ini risiko #1 dan masih hidup. |
| W2 | ~~Anti-cheat browser-side = theater~~ | **Ditutup.** ADR 003. Tapi jangan pernah slide balik ke klaim "anti-cheat" — itu pintu masuk satu pertanyaan juri yang mematikan. |
| W3 | **Honeypot 54%, bukan 100%** | Angka ini kuat untuk deck dan jujur untuk Q&A, tapi **bukan jaminan demo**. 29 dari 80 panggilan justru REFUSE. Demo harus pakai term `fictional_term` (efektivitas 100% di n=12 valid, tertinggi dari 4 trap) di model yang paling mudah terpancing. |
| W4 | **Penilaian reasoning tetap LLM-mediated** | Deterministic classification (ADR 002) menurunkan subjektivitas, verifier menangkap 65%. Sisanya tetap judgment call — akui di deck, jangan disembunyikan. |
| W5 | ~~Tidak ada fallback~~ | **Ditutup.** API-CONTRACTS §3. |
| W6 | **Semua artefak submisi masih Indonesia / belum ada** | UI, README, deck, video wajib Inggris (`../01-event-guidelines/04-rules-eligibility.md` §2). Lihat N11 — contoh respons AI di API-CONTRACTS masih Bahasa Indonesia. |
| W7 | **Tidak ada kode.** | Empat hari untuk 12 must-ship item (§6). Tidak ada jalan untuk menambah fitur baru setelah dokumen ini. |

### 2.3 OPPORTUNITIES

| # | Opportunity | Cara mengeksploitasi |
|---|-------------|---------------------|
| O1 | **Tidak ada pesaing yang ambil posisi "anti-AI" di kompetisi AI** | Paradoks yang memorable. Deck slide 1: *"Setiap AI study tool menjawab pertanyaan. Assay yang mempertanyakan jawabanmu."* |
| O2 | **Juri suka guardrail deterministik** | Honeypot = jebakan deterministik dengan klasifikasi terstruktur; hasilnya auditable (`honeypot_verdict` + `evidence_quotes` di report), bukan "AI bilang begitu". |
| O3 | **On-device ML sebagai bukti Google-stack di luar Gemini** | MediaPipe = produk Google, nol token, nol biaya inferensi, dan secara visual sangat meyakinkan di demo. Sudah diputuskan (ADR 003), bukan lagi usulan. |
| O4 | **Sudut B2B / verifikasi kompetensi** | Bootcamp dengan completion <15% dan sertifikat yang tidak bisa dipercaya = pain yang bisa dibayar. Juri venture/enterprise akan menanyakan ini (§10 Q10). |
| O5 | **Angka empiris sendiri sebagai bukti Technical Merit** | Sangat jarang tim hackathon punya hasil uji sendiri dengan n, model list, dan log mentah. Pakai ini di slide "Evidence" — 3 baris tabel, bukan 10 slide. |

### 2.4 THREATS

| # | Threat | Severity | Mitigation |
|---|--------|----------|------------|
| T1 | User pakai device kedua (HP) untuk browsing jawaban | 🔴 CRITICAL | Browser-side tidak berguna di sini. Satu-satunya layer yang benar-benar bekerja: honeypot (§7.1 Layer 4). |
| T2 | LLM terbaru menolak menjawab konsep fiktif | 🟠 HIGH | **Sudah diukur**: 25%-75% per model. Pin model, rotasi term dari katalog (ADR 005), siapkan cached scenario. |
| T3 | Juri menganggap "focus mode" terlalu mengekang / tidak aksesibel | 🟠 HIGH | Accessible Mode + framing integrity signal + skor ditandai `assisted_unverified` (§4). |
| T4 | Pesaing lain juga bikin adaptive learning platform | 🟡 MEDIUM | Moat = honeypot + calibration gap + adversarial positioning. "Adaptive quiz" saja tidak cukup. |
| T5 | Gemini rate limit / down saat demo | 🟠 HIGH | `DEMO_MODE=cached` dengan 2 skenario (sukses + copas-tertangkap). Non-negotiable. |
| T6 | **Focus Mode menelan Hari 3 dan demo jadi setengah jadi** | 🟠 HIGH | Baru di v2 (MediaPipe naik ke must-ship). Mitigasi: camera opsional, cached scenario tidak butuh kamera, blur = overlay 30 baris JS. Lihat N2. |
| T7 | **Scope berhenti di dokumen, bukan di kode** | 🔴 CRITICAL | Satu-satunya mitigasi: Hari 4 tidak boleh ada fitur baru. Titik. |

---

## 3. COMPETITOR DEEP-DIVE

### 3.1 Direct Competitors (platform belajar aktif yang sudah ada)

| Platform | Apa yang sudah mereka lakukan | Keunggulan Assay |
|----------|-------------------------------|------------------|
| **Khan Academy Khanmigo** | AI tutor berbasis Socratic method, 2+ tahun operasi, didanai Bill & Melinda Gates Foundation | **Kompetitor terberat.** Tapi: tidak ada gatekeeping, tidak ada deteksi integritas, tidak bisa upload PDF sendiri, tidak ada enforcement. |
| **Google Learn About** | Interactive AI tutor dari Google, pendekatan Socratic | Tanpa enforcement, tanpa gatekeeping. User bisa langsung minta jawaban — dan akan dapat. |
| **Quizlet AI** | Flashcard otomatis + practice test | Surface-level recall. Tidak ada interrogasi reasoning, tidak ada jejak penalaran. |
| **Coursera / Udemy AI** | Adaptive quiz setelah video | Pasif. User bisa nonton sambil scroll HP. Tidak ada friksi. |
| **Duolingo** | Gamifikasi + spaced repetition | Hanya bahasa. Model gamifikasinya (streak/XP) bisa dipinjam untuk engagement, bukan positioning. |
| **NotebookLM** | Summarize doc, generate podcast | Ini "the villain" dalam narasi Assay: enabler brain rot. Sebut namanya di deck — berani, dan juri tahu itu produk mereka. |
| **Foreman** (peserta AI Builder Cup 2026, Track 5) | "Honesty Canary": uji kejujuran **agen AI** dengan soal yang jawabannya sengaja tidak ada | DNA mekanisme sama dengan honeypot Assay. Bedanya satu kalimat: Foreman menguji kejujuran **agen**; Assay menguji kejujuran **manusia yang menyontek agen lain**. Sebut eksplisit — juri akan mengenali polanya dan menilai Assay sebagai cermin sisi-manusia. |
| **Chopdesk** (Track 1) | Heuristic offline fallback saat Gemini 429 | Bukan lawan (beda track), tapi patokan: Assay wajib punya kelas fallback yang sama. Sudah punya (API-CONTRACTS §3). |

### 3.2 Khanmigo Risk Assessment

Juri **pasti** bertanya: *"Apa bedanya dengan Khanmigo?"*

**Diferensiasi kritis (pakai urutan ini):**
1. Khanmigo **suggestive**, bukan **enforcement**. User bisa skip sesi Socratic kapan saja; Assay mengunci chapter sampai skor ≥ 75.
2. Khanmigo **tidak mendeteksi integritas**. Tidak ada honeypot, tidak ada sinyal fokus.
3. Khanmigo **tidak menerima dokumen user**. Tidak bisa "ujilah saya atas modul kuliah saya sendiri".
4. Khanmigo **tidak punya calibration gap** — jarak antara "merasa paham" dan "benar-benar paham" tidak pernah muncul.

**Yang wajib diakui di depan juri:** Khanmigo sudah berjalan 2+ tahun dengan riset efektivitas, didanai lembaga besar. Assay berumur 4 hari. Jangan klaim superioritas total — klaim ini: *"We build on a proven Socratic method and add the enforcement and integrity layer that nobody ships."* Mengakui batas justru menaikkan kredibilitas.

---

## 4. THE MOBILE-CHEATING PROBLEM & ML CAMERA — **DECIDED**

### 4.1 Problem Statement

Anti-cheat browser-side (`onblur`, `oncopy`, `user-select: none`) tidak berguna kalau:
- User membuka ChatGPT di HP sambil belajar di laptop
- User pakai second monitor / virtual desktop
- User mengetik ulang pertanyaan secara manual
- User memakai screen reader atau alat bantu aksesibilitas

### 4.2 Keputusan final (ADR 003 — Accepted, bukan lagi rekomendasi)

```
+-----------------------------------------------------------------+
|              FOCUS MODE — ON-DEVICE, NO VIDEO OUT               |
|                                                                  |
|  MediaPipe in-browser (client-side inference)                    |
|  --------------------------------------------------------------  |
|  Sinyal yang dideteksi:                                          |
|   - GAZE_DRIFT       head-pose/gaze menyimpang > ambang          |
|   - MULTIPLE_FACES   jumlah wajah > 1                            |
|   - TAB_BLUR         pindah tab / window kehilangan fokus        |
|   - CAMERA_OFF       kamera mati / tidak diizinkan               |
|                                                                  |
|  Yang dikirim ke server: HANYA event boolean + timestamp +       |
|  durasi. `video_transmitted: false` adalah field WAJIB.          |
|  Video/gambar/embedding TIDAK PERNAH meninggalkan device.        |
|                                                                  |
|  Saat sinyal menyala -> halaman AUTO-BLUR + flag `assisted`.     |
|  Blur = pencegah + penanda, BUKAN hukuman: skor tetap dihitung.  |
+-----------------------------------------------------------------+
```

**Konsekuensi yang harus diucapkan sendiri sebelum juri mengucapkannya:**
1. **Accessible Mode** mematikan kamera sepenuhnya (copy boleh, blur mati, waktu longgar). Skor tetap dihitung dan ditandai **`assisted_unverified`** — supaya sesi tanpa verifikasi tidak diam-diam dibaca sebagai "clean".
2. **Deteksi terikat device.** Akurasi MediaPipe turun di hardware murah, cahaya buruk, posisi kamera aneh. Sinyalnya **advisory, bukan authoritative**.
3. **False positive terkandung.** Melirik ke bawah untuk menulis catatan ≠ menyontek. Karena itu flag turun skor integritas + masuk laporan + bisa di-appeal, bukan auto-fail.
4. **Bukan klaim anti-cheat.** Tidak ada sistem yang cheat-proof. Yang Assay jual: biaya menyontek jadi lebih mahal dari belajar.

### 4.3 Kenapa ini menang di rubrik (bukan cuma fitur)

| Alasan | Rubrik yang kena |
|---|---|
| MediaPipe = Google stack di luar Gemini | Technical Merit (40%) |
| Nol token LLM, nol biaya inferensi per frame | Technical Merit / Skalabilitas |
| Live face tracking yang menangkap user melirik HP = demo visual paling memorable | Innovation (25%) |
| On-device + `video_transmitted: false` = privacy claim yang dibacking kontrak, bukan janji | UX & Solution Design (10%) + Q&A Q4 |
| Accessible Mode + `assisted_unverified` = tidak mengorbankan pengguna disabilitas | UX & Solution Design (10%) |

### 4.4 Penghematan token dengan ML & telemetry client-side

| Task | Tanpa ML | Dengan ML/telemetry client-side | Hemat |
|------|----------|--------------------------------|-------|
| Deteksi user membaca vs skip | Gemini mengevaluasi waktu baca vs panjang teks (1 call/chapter) | Scroll + dwell telemetry di frontend | ~500 token/chapter |
| Deteksi copy-paste | Gemini membandingkan gaya tulisan (1 call) | `paste_detected` + `keystroke_cpm` yang **sudah ada di kontrak** (API-CONTRACTS §2.5) | ~800 token/eval |
| Kecurangan device kedua | Tidak mungkin tanpa kamera | MediaPipe gaze/head-pose | N/A (mustahil tanpa ML) |
| Pre-filter sebelum deep eval | Semua jawaban dikirim ke Gemini | Rule-based filter (panjang, keyword, durasi) → hanya yang suspicious dikirim untuk deep eval | ~60% |

---

## 5. JUDGING CRITERIA OPTIMIZATION

Rubrik resmi (`../01-event-guidelines/05-judging-criteria.md`): Technical Merit & Gen AI 40% · Problem Alignment & Impact 25% · Innovation & Creativity 25% · UX & Solution Design 10%.

### 5.1 Technical Merit & Gen AI Implementation (40%) — THE KING MAKER

| Sub-kriteria | Yang juri cari | Yang harus ditunjukkan | Gap sekarang |
|---|---|---|---|
| Meaningful Use of Gen AI | AI = mesin inti, bukan gimmick | Socratic interrogator + honeypot classifier + syllabus synthesis = AI menggerakkan seluruh produk | ✅ Kuat |
| Ketepatan Arsitektur Sistem | Modular, deterministik, aman | ADR 001-005 **sudah ada**; state machine per chapter; JSON schema terkunci | ⚠️ ADR beres, **diagram arsitektur belum ada** |
| Skalabilitas & Ketahanan | Error handling, fallback, latency | `DEMO_MODE=cached` + auto-trigger 429/500/503 (API-CONTRACTS §3) | ✅ Ditutup di v2 |
| Advanced AI Techniques | Bukan wrapper prompt | Structured output (4/4 valid JSON), model routing Flash/Pro, verifier loop, MediaPipe, PDF-RAG | ✅ Kuat **kalau dieksekusi** |
| Eval harness + angka | Benchmarks folder, bukan klaim | Sudah punya angka (n=80, n=48, 13/20, 4/4) — tinggal dibungkus jadi `benchmarks/` + `eval/` yang bisa dijalankan ulang | ⚠️ Angka ada, harness belum |

**Action items untuk 40%:**
1. `benchmarks/` + `eval/` yang bisa dijalankan ulang, dengan README singkat dan output tersimpan. Angka tanpa harness = klaim.
2. Diagram arsitektur container (frontend / API / Gemini / Firestore / MediaPipe on-device) — satu PNG, jangan tiga.
3. Tabel ADR 001-005 di README dengan satu baris "apa yang ditolak dan kenapa".

### 5.2 Problem Alignment & Impact (25%)

| Sub-kriteria | Gap | Fix |
|---|---|---|
| Friksi spesifik Track 4 | ✅ Kuat — brain rot / konsumsi pasif | Pakai bahasa problem statement panitia di slide 2. |
| Quantifiable impact | ⚠️ Angka masalah ada (95%, 67%, PISA, 9 juta gap); **angka produk belum** (belum ada klaim retensi yang bisa dibuktikan) | Jangan mengarang klaim retensi. Pakai yang bisa dipertahankan: *kalibrasi* (calibration gap) dan *integritas* (54% honeypot) sebagai metrik yang memang diukur Assay. |
| Relevansi JAPAC | ✅ Ditutup di v2 §2.3 (World Bank 9 juta talenta digital; bootcamp completion <15%) | Tambahkan satu baris "kenapa Indonesia/SEA dulu" di deck. |
| Target user spesifik | ⚠️ Masih dua arah (B2C demo + B2B story) | Untuk deck: **demo B2C, uangnya B2B**. Satu kalimat, jangan dua pitch. |

### 5.3 Innovation & Creativity (25%)

| Sub-kriteria | Status | Aksi |
|---|---|---|
| Diferensiasi & orisinalitas | ✅ Honeypot pedagogis + AI-as-enforcer + calibration gap. Tiga hal yang tidak ada di produk existing. | Sebut Foreman sebagai cermin filosofis (§3.1). |
| Beyond superficial | ✅ Structured output + deterministic classification + RAG hybrid + on-device multimodal | Tunjukkan PDF-RAG page-anchor sebagai bagian dari mekanisme honeypot, bukan sebagai fitur tambahan. |
| Multimodal | ✅ MediaPipe (diputuskan) | Demo harus memperlihatkan event-nya hidup, bukan hanya slide. |

### 5.4 User Experience & Solution Design (10%)

**Tension yang harus di-frame, bukan disembunyikan:** Assay sengaja penuh friksi (gate, blur, timer), sementara juri menilai kemudahan.

> *"Friction is the feature, not the bug. We gate chapters the way a gym gates results — the resistance is the point."*

Dua hal yang menutup kritik UX:
1. **Accessible Mode** yang benar-benar berfungsi (kamera off, copy boleh, waktu longgar) — bukan toggle kosmetik.
2. **Calibration slider** — satu momen 10 detik yang membuat user merasa diukur, bukan dihakimi. Ini juga fitur termurah dengan dampak terbesar.

Wajib ada: 1 slide "Guided Tour" atau onboarding 3 langkah supaya juri tidak tersesat saat mencoba live.

---

## 6. SCOPE FINAL — MUST SHIP vs CUT (selaras PRD v2)

### 6.1 🟢 MUST SHIP (non-negotiable, semuanya ada di PRD v2 §3)

| # | Fitur | Justifikasi | Effort |
|---|-------|-------------|--------|
| 1 | **Intake screen** (intent + role selector + PDF opsional) | Entry point. Tanpa ini tidak ada produk. | Medium |
| 2 | **Realtime checklist generation** (+ user edit check/uncheck) | Momen personalisasi pertama; item tercentang = bahan silabus. | Medium |
| 3 | **Syllabus synthesis** (chunk → chapter berstruktur + reference enrichment, PDF-RAG page-anchor) | PDF-RAG yang bikin klaim honeypot bisa diverifikasi ("istilah ini tidak ada di halaman mana pun"). | High |
| 4 | **Gated chapter reader** (chapter linear, `next` LOCKED sampai skor ≥ 75) | Core differentiator. Tidak ada tombol ringkasan. | Low-Medium |
| 5 | **Select-word Socratic ask** (+ suggested questions multi-kata, `gave_direct_answer: false`) | Fitur baru yang membuktikan tesis: AI balik nanya. | Medium |
| 6 | **Interview quiz multi-turn 2-3 ronde** (pertanyaan inferensial, adaptive follow-up) | Jantung produk. | Medium |
| 7 | **Honeypot injection + klasifikasi 4 nilai** (`CRITICAL_REJECTION +2` / `AI_HALLUCINATION_COPYPASTE −2` / `UNVERIFIED_HONEST 0` / `EVASIVE −1`) — **dimensi skor, bukan gate** | "Wow moment" demo. Harus jalan sempurna. | Medium |
| 8 | **Calibration** (prediksi sebelum reveal) + `calibration_gap` | Fitur termurah, dampak terbesar, tidak ada di kompetitor. | Low |
| 9 | **Single score per chapter + final report** (skor lintas chapter, tren calibration gap, integrity log, honeypot verdict) | Bukti bahwa penilaian benar-benar terjadi. | Low |
| 10 | **DEMO_MODE=cached** (2 skenario wajib: success flow + caught flow) | Kalau API mati saat demo = game over. | Low |
| 11 | **Focus Mode camera** (MediaPipe on-device, 4 event boolean, auto-blur, Accessible Mode) | Technical Merit + Innovation + demo visual. | Medium |
| 12 | **Eval harness + angka + ADR + diagram arsitektur** | Ini yang mengubah "klaim" jadi "bukti" di rubrik 40%. | Medium |

**Catatan:** verifier loop + appeal path masuk must-ship meski murah (endpoint + satu UI). PRD §8 menyebut verifier sebagai wajib; appeal sudah ada di kontrak §2.8 dan di PRD §4.6.

### 6.2 🟡 SHOULD HAVE (kalau waktu masih ada — jangan dipaksa)

| # | Fitur | Justifikasi | Effort |
|---|-------|-------------|--------|
| 13 | **`paste_detected` + `keystroke_cpm` telemetry** | **Sudah ada di API-CONTRACTS §2.5.** Tinggal dikirim dari frontend. Sinyal integritas termurah yang tersedia. | Low |
| 14 | **Response pressure timer** (sinyal, bukan auto-fail) | PRD §4.5. Ngukur waktu mikir user, bukan waktu tunggu model. | Low |
| 15 | **Google Search grounding 1-2 chapter** (hasil di-cache) | Menambah kredibilitas "reference enrichment". | Medium |
| 16 | **No-PDF path** (`source: role_taxonomy_generated`) | Menyelamatkan demo kalau PDF gagal parse. Jangan dipakai sebagai alur utama demo. | Medium |
| 17 | **SSE streaming checklist** | Kalau polling sudah cukup untuk demo, polling lebih murah dan tidak ada risiko. | Medium |

### 6.3 🔴 CUT (roadmap slide saja — jangan disentuh Hari 4)

| # | Fitur | Alasan |
|---|-------|--------|
| 18 | Monaco + Piston + TDL (coding arena) | Tidak muat 4 hari; bukan wedge. |
| 19 | DAG Skill Tree visual (ReactFlow) | Tidak pembeda; chapter stepper linear gratis dan lebih jelas. |
| 20 | Dual-metric (2 skor terpisah) | Digantikan single score + calibration gap (lebih murah, lebih kuat). |
| 21 | Voice / Gemini Live | Latency + biaya berisiko di live. |
| 22 | Auth kompleks / multi-user | 1 sesi demo cukup. |
| 23 | Multi-source input (video/audio) | PDF cukup. |
| 24 | Excalidraw / evaluasi diagram | Scope creep. |
| 25 | Keystroke dynamics engine penuh | `paste_detected` saja sudah cukup (#13). |

### 6.4 Feature → Rubrik

```
JUDGING RUBRIC (100%)
|
+-- Technical Merit 40% ....... Socratic interview + verifier, structured output,
|                              MediaPipe, eval/ + benchmarks, cached fallback
+-- Problem & Impact 25% ...... angka masalah (HEPI/RAND/PISA), JAPAC 9 juta gap,
|                              satu B2B story (bukan dua pitch)
+-- Innovation 25% ............ honeypot + 54% evidence, calibration gap,
|                              select-word Socratic, AI-as-enforcer
+-- UX & Solution Design 10% .. Accessible Mode + assisted_unverified, calibration
                               slider, guided tour, SSE streaming
```

---

## 7. THREAT MITIGATION PLAYBOOK

### 7.1 Threat: User menyontek dengan device kedua

| Layer | Taktik | Efektivitas |
|-------|--------|-------------|
| **Layer 1 — Paste/telemetry** (client) | `paste_detected` + `keystroke_cpm` + durasi (sudah di kontrak). Jawaban panjang muncul <2 detik = flag. | 🟢 Tinggi untuk deteksi paste |
| **Layer 2 — Response time analysis** (backend) | Pertanyaan inferensial dijawab <15 detik dengan paragraf panjang = suspicious. | 🟡 Medium — false positive untuk fast typist |
| **Layer 3 — MediaPipe focus signals** (client ML) | `GAZE_DRIFT` / `MULTIPLE_FACES` / `TAB_BLUR` → auto-blur + flag `assisted`. | 🟡 Medium — banyak false positive, advisory |
| **Layer 4 — Honeypot** (AI-level) | Satu-satunya defense yang benar-benar bekerja terhadap LLM eksternal, apa pun device-nya. **54% halusinasi terukur; `fictional_term` 100% efektif (n=12 valid).** | 🟢 Tinggi (bukan 100% di populasi) |
| **Layer 5 — Consistency cross-check** (AI-level) | Ronde berikutnya menanyakan konsep yang sama dengan framing berbeda. Jawaban kontradiktif = "inconsistent understanding". | 🟢 Tinggi |
| **Layer 6 — PDF-RAG anchor** (AI-level) | Klaim user diverifikasi ke halaman dokumen. Istilah/kutipan yang tidak ada di halaman mana pun = sinyal. | 🟢 Tinggi (kalau demo pakai PDF) |

**Verdict:** jangan bergantung pada satu layer. Dan jujur ke juri: **no system is cheat-proof** — yang Assay lakukan adalah membuat biaya menyontek lebih tinggi daripada biaya belajar. Kalimat yang dipakai di deck dan Q&A: *"We don't prevent cheating. We make it more effort than learning."*

### 7.2 Threat: Honeypot gagal (LLM modern menolak halusinasi)

**Status: sudah diukur, bukan lagi asumsi.** n=80 panggilan, 4 model:

| Model | Halusinasi | Refuse | Hedge | Error | Latensi avg |
|---|---|---|---|---|---|
| ag/gemini-3.8-flash-medium | **75%** | 3 | 2 | 0 | 13s |
| z/deepseek-v4-pro | 70% | 4 | 2 | 0 | 30s |
| z/deepseek-v4-flash | 45% | 10 | 0 | 1 | 22s |
| z/deepseek-v4.1-flash | **25%** | 12 | 1 | 2 | 34s |
| **TOTAL** | **54%** | 29 | 5 | 3 | 25s |

Efektivitas per jenis trap (n=48): `fictional_term` **100%** (10 comply / 0 pushback / 2 error, n=12 valid) · `trap_number` 58% · `false_premise` 25% · `over_claim` 25%.

**Mitigasi yang harus dieksekusi:**
1. **Pin model di demo.** Jangan pernah demo di deepseek-v4.1-flash (25%). Model yang paling mudah terpancing sudah teridentifikasi.
2. **Pakai `fictional_term`, bukan `false_premise`/`over_claim`.** 25% terlalu lemah untuk momen yang harus jalan sempurna.
3. **Rotasi term dari katalog (ADR 005).** Sediakan 20-30 term per domain supaya demo tidak bergantung pada satu istilah.
4. **Jangan pernah tulis "100%" atau "terbukti selalu" di deck.** Tulis 54% (n=80) — angka jujur lebih kuat daripada superlatif, dan juri teknis akan menghargai n-nya.
5. **Cached scenario sebagai jaring pengaman.** Kalau LLM live-nya menolak, caught flow tetap ada di `DEMO_MODE=cached`.

### 7.3 Threat: Juri merasa UX terlalu mengekang

1. Tampilkan **Accessible Mode** secara eksplisit di UI (kamera off, copy boleh, waktu longgar) dan jelaskan konsekuensinya: skor ditandai `assisted_unverified`.
2. Frame friksi sebagai **pedagogical design pattern**: *"Desirable Difficulties"* (Bjork) — kesulitan yang disengaja meningkatkan retensi jangka panjang.
3. Buka dengan disclaimer: *"This product is intentionally hard. That's the point."*
4. Jangan pernah menyebut kata "anti-cheat" sebagai klaim keamanan. Sebut **focus & integrity signal**.

### 7.4 Threat: Gemini down / rate limited saat demo

1. Trigger: `DEMO_MODE=cached` ATAU header `x-demo-mode: cached` ATAU error 429/500/503 (API-CONTRACTS §3).
2. **Dua skenario wajib:**
   - **Success flow** — user kritis menolak honeypot → `CRITICAL_REJECTION`, skor tinggi, chapter unlock.
   - **Caught flow** — user copas jawaban LLM luar → `AI_HALLUCINATION_COPYPASTE`, skor turun, integrity flag.
3. Banner `LOCAL_DETERMINISTIC_CACHE` **boleh tampil di depan kamera** — itu fitur ketahanan, bukan glitch. Kalimatnya: *"Gemini mocked for resilience."*
4. Cache juga menyimpan hasil grounding eksternal supaya demo tidak bergantung jaringan.

---

## 8. FEATURE PRIORITY & BOBOT INTERNAL

### 8.1 Kontribusi per fitur ke rubrik juri

| Fitur | Tech Merit (40%) | Problem Impact (25%) | Innovation (25%) | UX (10%) | Total | Priority |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|
| Socratic interview multi-turn + verifier | ★★★★★ | ★★★ | ★★★ | ★★ | **30%** | P0 |
| Honeypot trap + klasifikasi deterministik | ★★★★ | ★★ | ★★★★★ | ★ | **25%** | P0 |
| Syllabus + PDF-RAG + gated reader | ★★★★ | ★★★★ | ★★★ | ★★★ | **18%** | P0 |
| Focus Mode MediaPipe (on-device) | ★★★★ | ★★ | ★★★★ | ★★ | **10%** | P0 |
| Eval harness + benchmarks + ADR/diagram | ★★★★★ | ★ | ★ | ★ | **8%** | P0 |
| Cached fallback mode | ★★★★★ | ★ | ★ | ★★★★ | **5%** | P0 |
| Calibration + report | ★★ | ★★★ | ★★★★ | ★★★★ | **4%** | P0 |
| Paste/telemetry + response timer | ★★★ | ★ | ★★ | ★★ | **—** | P1 |

### 8.2 Effort vs Impact (dibaca sebagai jadwal)

Semua P0 di kuadran **kiri** (Socratic+verifier, honeypot, syllabus+PDF-RAG+gate, cached fallback, calibration+report) harus selesai sebelum Hari 4. Focus Mode dan eval harness ada di kanan-bawah-impact-tinggi — keduanya punya jaring pengaman (camera opsional; angka sudah ada), jadi keduanya boleh turun ke bentuk minimal kalau Hari 3 habis. Monaco/Piston dan DAG visual ada di kanan-atas-effort: **cut**, tidak dibangun dalam bentuk apa pun.

---

## 9. WHAT THE PRD GETS WRONG (v2 — diperbarui)

Baris yang **sudah diperbaiki di v2** tetap dicantumkan supaya tidak ada yang menghidupkan lagi masalahnya.

| Bagian | Masalah | Status | Fix |
|---|---|---|---|
| §1.2 v1 — buzzword "High-Friction, High-Reward" tanpa definisi operasional | Slogan, bukan spesifikasi | ⚠️ **PARTIAL** | PRD v2 §3 mendefinisikannya lewat flow (chapter terkunci, tidak ada tombol ringkasan, gate skor ≥75), tapi frasenya masih muncul di §1.2 tanpa satu kalimat operasional. Tambahkan definisi eksplisit di deck notes. |
| §3.3 v1 — Monaco + Piston + TDL | Scope project tersendiri | ✅ **RESOLVED** | Cut ke roadmap (PRD v2 §8); state `DEBUG_CHALLENGE` dihapus dari kontrak. |
| §3.4 v1 — anti-cheat browser-side dijual sebagai keamanan | Security theater | ✅ **RESOLVED** | ADR 003 menolaknya secara eksplisit; diganti Focus Mode + framing integrity signal. |
| §4 v1 — 4 developer tanpa kontrak API | Integrasi mustahil | ✅ **RESOLVED** | `API-CONTRACTS.md` v2 LOCKED; tim jadi 3 dev dengan pembagian per-pilar. |
| §5 v1 — timeline mulai 14 Okt, dokumen ditulis 13 Okt malam | Hari 1 hilang untuk planning | ✅ **RESOLVED** | Hari 0 (14 Okt) dipakai untuk kontrak + angka; **sudah selesai hari ini**. |
| §6 v1 — honeypot `trigger_round: 2` hardcoded | Honeypot tidak pernah kena kalau interview 1 ronde | ❌ **OPEN** | API-CONTRACTS §2.5 masih menaruh honeypot di `turn_index: 2`. Paksa minimum 2 ronde sebelum `finalize`, atau inject di ronde 1 untuk interview pendek. **Uji jalur ini sebelum merekam video.** |
| §7 v1 — winning playbook tanpa Q&A defense | Juri akan menantang, tim gelagapan | ✅ **RESOLVED** | §10 dokumen ini. |

### Temuan BARU di v2 (yang belum ada di audit v1)

| # | Temuan | Severity | Fix |
|---|---|---|---|
| N1 | **Aritmatika §5 tidak menutup.** PRD v2 sendiri menulis ~14.75 dev-day vs ~9.6 kapasitas. Cut list §8 berisi item roadmap (Monaco/DAG/voice), bukan item yang sudah dihitung di 14.75. | 🔴 CRITICAL | Pilih satu: (a) potong lagi 5 dev-day dari flow (kandidat: SSE → polling, no-PDF path, appeal UI, Google Search grounding), atau (b) turunkan target demo ke 2 chapter, bukan 3, atau (c) terima 12 jam kerja/hari dan tulis itu di jadwal. Yang tidak boleh: berpura-pura defisitnya tidak ada. |
| N2 | **Focus Mode naik ke must-ship tapi jadwalnya Hari 3**, bareng scoring + calibration + report + cached fallback. Itu empat hal berat di satu hari. | 🟠 HIGH | Bangun Focus Mode sebagai komponen mandiri lebih dulu (kamera → event → blur), integrasikan terakhir. Skenario cached tidak memerlukan kamera sama sekali. |
| N3 | **Empat "fitur wajib riset" (eval harness, verifier, calibration, cached fallback) = 3.5 dev-day** menurut PRD sendiri, dan semuanya jatuh di Hari 3-4, saat tim paling lelah. | 🟠 HIGH | Pindahkan eval harness ke Hari 1-2 (dia tidak butuh UI, cuma butuh endpoint yang sudah jadi). Kalau ditunda ke Hari 4, dia akan hilang. |
| N4 | **Honeypot bukan jaminan demo.** 54% agregat; 25% di salah satu model. | 🟠 HIGH | Pin model (gemini-flash-medium 75%), pakai `fictional_term` (100% di n=12), rotasi term (ADR 005), siapkan cached caught-flow. |
| N5 | **Kata "anti-cheat" masih muncul di PRD v2** (§3 Step 5 baris "Anti-cheat feature", §5 diagram "anti-cheat"). ADR 003 sudah menolak framing itu. | 🟡 MEDIUM | Ganti jadi "Focus Mode / integrity signal" di seluruh dokumen. Inkonsistensi kecil, tapi juri membaca dokumen. |
| N6 | **UI wajib Inggris, tapi contoh respons AI di API-CONTRACTS masih Bahasa Indonesia** (§2.4 `"Sebelum gw jawab — menurut kamu…"`, §2.5 pertanyaan interview Bahasa Indonesia). | 🟡 MEDIUM | Kalau demo merekam UI berbahasa Inggris dengan balasan AI berbahasa Indonesia, itu terlihat belum matang. Tentukan bahasa runtime (rekomendasi: Inggris, karena submisi wajib Inggris) dan perbarui contoh di kontrak + prompt. |
| N7 | **Tidak ada diagram arsitektur.** ADR sudah bagus, tapi rubrik menyebut "Ketepatan Arsitektur Sistem". | 🟡 MEDIUM | Satu diagram container, taruh di README + slide 6. Setengah hari kerja, dampak besar ke rubrik 40%. |
| N8 | **`assisted` vs `assisted_unverified` belum dipakai konsisten.** PRD §4.5 menyebut flag `assisted` untuk dua situasi berbeda (deteksi curang vs Accessible Mode). | 🟡 MEDIUM | Pakai pembagian dari ADR 003: deteksi → `assisted`; kamera off → `assisted_unverified`. Kontrak §2.7 sudah benar; samakan PRD dan UI. |
| N9 | **Disiplin angka — RESOLVED.** Deck v1 menulis "91.3% / 640ms" tanpa sumber (sudah dibuang). Selisih `fictional_term` (log lama 67%/90% vs kanonik 100%) sudah ditelusuri: angka 67% salah karena menghitung ERROR sebagai PUSHBACK. Angka kanonik = 10 comply / 0 pushback / 2 error (n=12 valid). | 🟢 RESOLVED | Semua dokumen sudah pakai 100% (n=12) + sebutkan n-nya. Jangan pakai 67%/90% lagi. |
| N10 | **Posisi kompetitor bisa salah dibaca.** FOREMAN dan CHOPDESK beda track — mereka patokan kualitas, bukan lawan head-to-head. | 🟡 MEDIUM | Di deck, sajikan mereka sebagai "patokan kualitas" dan ambil pelajarannya (honesty canary, fallback), bukan sebagai lawan yang dikalahkan. |
| N11 | **Semua artefak submisi (UI copy, README, deck, video) masih nol.** Wajib Inggris. | 🟠 HIGH | Masukkan copywriting Inggris ke budget Hari 4 secara eksplisit, bukan sebagai "sisa waktu". |
| N12 | **Default state Focus Mode belum ditentukan.** Kalau default kamera mati, momen demo paling visual hilang; kalau default nyala, kritik aksesibilitas datang. | 🟡 MEDIUM | Default: kamera **nyala** saat interview quiz, dengan toggle Accessible Mode yang terlihat jelas di layar. Jelaskan konsekuensi skor di UI saat toggle ditekan. |

---

## 10. JURI Q&A DEFENSE SCRIPT

Pertanyaan yang hampir pasti ditanyakan, dengan jawaban yang harus dihafal.

### Q1: "Apa bedanya ini dengan Khanmigo / Google Learn About?"
> **A:** "Khanmigo dan Learn About adalah *suggestive tutors* — mereka bertanya secara Socratic, tapi menerima jawaban apa pun dan lanjut. Assay adalah *enforcement engine*: chapter berikutnya terkunci sampai reasoning kamu lolos evaluasi, skor ≥ 75. Selain itu, Assay menyuntik konsep fiktif untuk menangkap user yang meng-outsource pemikirannya ke LLM eksternal — dan kami mengukurnya: **54% halusinasi dari 80 panggilan ke 4 model frontier**. Kami tidak mengklaim mengalahkan Khanmigo; kami membangun di atas metode Socratic yang sudah terbukti dan menambahkan lapisan enforcement dan integritas yang belum ada yang mengirimkannya."

### Q2: "Anti-cheat browser-side itu sepele di-bypass. Apa yang sebenarnya mencegah kecurangan?"
> **A:** "Betul, dan karena itu kami tidak memakainya. ADR 003 menolak `user-select: none` dan blur paksa sebagai security theater. Lapisan yang benar-benar bekerja ada di level AI: (1) honeypot — 54% terukur, dan jenis trap terkuat kami (fictional_term) memancing jawaban yakin di 100% panggilan valid (n=12); (2) cross-check konsistensi antar ronde; (3) verifikasi klaim ke halaman dokumen lewat PDF-RAG. Focus Mode MediaPipe kami sebut *integrity signal*, bukan keamanan — sinyalnya advisory. Tidak ada sistem yang cheat-proof; kami membuat menyontek lebih mahal daripada belajar."

### Q3: "Bagaimana kalau AI salah menilai jawaban yang sebenarnya benar?"
> **A:** "Tiga lapis. Satu, penilaian berjalan di atas JSON schema dengan klasifikasi deterministik (ADR 002) — bukan free-text judge, dan setiap penilaian membawa `evidence_quotes` plus nilai `confidence`. Dua, ada verifier model kedua: pada pengujian kami, dia menangkap **13 dari 20 halusinasi (65%)** — kami jujur bahwa 35% lolos. Tiga, ada appeal path: user bisa membantah skor, sistem menandai `revised` atau `uncertain`. Semua jejak penalaran tersimpan untuk audit."

### Q4: "Bagaimana privasi user? Anda menyalakan kamera."
> **A:** "Video tidak pernah meninggalkan device. Inferensi MediaPipe jalan di browser; yang dikirim ke backend hanya event boolean — `GAZE_DRIFT`, `MULTIPLE_FACES`, `TAB_BLUR`, `CAMERA_OFF` — dengan timestamp dan durasi. Payload-nya wajib membawa `video_transmitted: false`, dan itu tertulis di kontrak API kami, bukan sekadar janji di slide. Kami tidak punya pipeline video, jadi tidak ada retensi biometrik, tidak ada consent flow video, dan tidak ada klasifikasi high-risk AI Act untuk remote proctoring. Accessible Mode mematikan kamera sepenuhnya; skornya tetap dihitung dan ditandai `assisted_unverified` supaya laporannya jujur."

### Q5: "Ini terlalu mengekang. User akan frustrasi dan berhenti."
> **A:** "Friksinya sengaja — kami mengacu ke riset 'Desirable Difficulties' (Bjork): kesulitan yang disengaja meningkatkan retensi jangka panjang. Yang penting, friksi kami terbatas dan transparan: satu gate per chapter, ambang 75, dan ada Accessible Mode yang mematikan kamera, mengizinkan copy, dan melonggarkan waktu. Kami tidak menjual kenyamanan; kami menjual bukti pemahaman. Kalau user mau ringkasan instan, NotebookLM sudah ada."

### Q6: "54% itu bukan 100%. Bagaimana kalau LLM-nya menolak menjawab istilah fiktif Anda?"
> **A:** "Betul, dan itu sebabnya kami mengukurnya sebelum membangun. Dari 80 panggilan ke 4 model: 43 berhalusinasi, 29 menolak, 5 ragu, 3 error. Kami juga tahu model mana yang paling mudah terpancing — 75% di satu model, 25% di model lain — jadi kami memilih model dan jenis trap berdasarkan data, bukan harapan. Kami punya katalog term deterministik dengan variasi (ADR 005) supaya tidak bisa dihafal, dan ada cached scenario kalau live-nya gagal. Di deck kami menulis 54%, bukan 100%. Angka yang bisa ditelusuri lebih berguna daripada superlatif."

### Q7: "Bukankah ini cuma proctoring / pengawasan?"
> **A:** "Bukan. Proctoring mengirim video ke server dan membangun pipeline biometrik; kami menolak itu karena biaya privasinya permanen dan keuntungan deteksinya marginal di skala kami. Kami memantau fokus, bukan orang: sinyalnya boolean, inferensinya on-device, dan konsekuensinya adalah flag plus auto-blur — bukan larangan, bukan laporan ke institusi. Dan kami tidak pernah menyebut ini anti-cheat."

### Q8: "Kalau tidak ada PDF yang di-upload, produk ini masih jalan?"
> **A:** "Jalan. Chapter di-generate dari role taxonomy plus grounding, dan ditandai `source: role_taxonomy_generated` supaya jelas asalnya. Tapi kami jujur: jalur PDF adalah yang paling kuat, karena PDF-RAG memberi page-anchor — dan page-anchor itulah yang membuat klaim honeypot bisa diverifikasi ('istilah ini tidak ada di halaman mana pun modul kamu')."

### Q9: "Ini kan cuma belajar. Model bisnisnya apa?"
> **A:** "Demo-nya B2C, tapi yang membayar adalah institusi. Bootcamp dengan completion rate di bawah 15% dan sertifikat yang tidak lagi dipercaya butuh bukti kompetensi, bukan nilai. Assay memberi mereka skor reasoning per chapter, tren calibration gap, dan integrity log yang bisa diaudit. Relevansi JAPAC-nya konkret: gap 9 juta talenta digital (World Bank), dan lulusan yang tidak terverifikasi adalah masalah yang dibayar oleh industri."

### Q10: "Kenapa pakai MediaPipe, bukan Gemini Vision?"
> **A:** "Tiga alasan. Satu, privasi: tidak ada video yang dikirim, jadi tidak ada pipeline biometrik. Dua, biaya: nol token untuk deteksi fokus, dan deteksi berjalan tiap frame tanpa biaya API. Tiga, latency: tidak ada round-trip jaringan untuk sinyal yang harus instan. Trade-off-nya kami akui: akurasi terikat kualitas device dan cahaya, jadi sinyalnya advisory — dan itu sebabnya flag-nya memengaruhi skor integritas plus bisa di-appeal, bukan menggagalkan sesi."

---

## 11. FINAL RECOMMENDATIONS

1. **TUTUP ARITMATIKA HARI INI, BUKAN BESOK.** PRD v2 §5 sendiri menunjukkan defisit ~5 dev-day (14.75 vs 9.6). Pilih satu jalan: potong lagi, turunkan target jadi 2 chapter, atau tambah jam kerja dan tulis di jadwal. Setiap fitur baru setelah dokumen ini = fitur yang mengorbankan gate, scoring, atau fallback.
2. **PIN MODEL DAN TERM HONEYPOT SEKARANG.** `fictional_term` (100% di n=12), model paling mudah terpancing (75%), rotasi dari katalog (ADR 005). Jangan pernah demo di model 25%.
3. **FOKUS MODE: BANGUN SEBAGAI KOMPONEN MANDIRI.** Kamera → event → auto-blur → flag, tanpa menunggu integrasi penuh. Skenario cached tidak butuh kamera, jadi demo punya jaring pengaman ganda.
4. **EVAL HARNESS PINDAH KE HARI 1-2.** Angka sudah ada (54%, 100%, 65%, 4/4); harness-nya hanya perlu membungkus dan menjalankannya ulang. Ini rubrik 40% dan paling sering hilang di Hari 4.
5. **CACHED FALLBACK DARI HARI 1.** Dua skenario (success + caught). Ini asuransi hidup-mati demo.
6. **JANGAN PERNAH BILANG "ANTI-CHEAT".** Bilang "Focus Mode / integrity signal". Perbaiki juga kata itu di PRD §3/§5 (N5) supaya dokumen dan presentasi konsisten.
7. **SAMAKAN BAHASA SEBELUM MEREKAM VIDEO.** UI, AI reply, README, deck, video = Inggris. Contoh respons Bahasa Indonesia di API-CONTRACTS §2.4/§2.5 harus diganti, kalau tidak demo akan terlihat campur-campur (N6).
8. **TAMBAHKAN SATU DIAGRAM ARSITEKTUR.** Setengah hari kerja, langsung terasa di rubrik "Ketepatan Arsitektur Sistem" (N7).
9. **UJI JALUR HONEYPOT 1 RONDE.** Temuan v1 yang masih OPEN: kalau user `finalize` setelah satu ronde, honeypot tidak pernah ter-inject. Paksa minimum 2 ronde.
10. **SIAPKAN Q&A.** Kalau tim gelagapan saat ditanya "apa bedanya dengan Khanmigo?" atau "54% itu bukan 100%", keunggulan teknis tidak akan menyelamatkan. Hafalkan §10, terutama Q2, Q4, Q6.
11. **HARI 4 = FREEZE.** Tidak ada fitur baru, tidak ada refactor besar. Hanya deploy, rekam, tulis deck, submit sebelum 20:00 UTC+8.
12. **AUDIT DIRI TERAKHIR, 1 JAM.** Buka PRD §3 flow dan cek satu per satu: apakah tiap langkah bisa ditunjukkan hidup di depan kamera? Yang tidak bisa, pindahkan ke slide roadmap — jangan dipaksakan.

---

## 12. EVIDENCE BASE (angka kanonik — jangan dikarang)

Sumber tunggal: `../reza-research/parts10/HASIL-TES-EMPIRIS.md` (gateway lokal, 14 Okt 2026 20:18, workers=5). Log mentah per-panggilan ada di `../reza-research/parts10/results/*.jsonl`.

| Metrik | Angka | n | Catatan |
|---|---|---|---|
| Honeypot hallucination rate (agregat) | **54%** | 80 panggilan, 4 model | 29 REFUSE, 5 HEDGE, 3 ERROR |
| — ag/gemini-3.8-flash-medium | 75% | 20 | **Model paling mudah terpancing — pin untuk demo** |
| — z/deepseek-v4-pro | 70% | 20 | Latensi 30s |
| — z/deepseek-v4-flash | 45% | 20 | 1 error |
| — z/deepseek-v4.1-flash | 25% | 20 | **Jangan dipakai di demo** |
| Trap efektivitas: fictional_term | **100%** (10 comply / 0 pushback / 2 error) | 12 valid | Trap terkuat — pakai ini (n kecil, baca sebagai "jalan", bukan angka presisi) |
| Trap efektivitas: trap_number | 58% | 48 | |
| Trap efektivitas: false_premise | 25% | 48 | Terlalu lemah untuk demo |
| Trap efektivitas: over_claim | 25% | 48 | Terlalu lemah untuk demo |
| Verifier loop menangkap halusinasi | **13/20 (65%)** | 20 | 4 lolos, 3 tidak jelas → residual risk nyata |
| Structured output valid JSON | **4/4 (100%)** | 4 | Klaim kuat, tapi n kecil — jangan dilebihkan |

**Aturan angka:**
1. Semua angka di deck, README, dan video harus bisa ditelusuri ke tabel di atas atau ke `eval/` yang bisa dijalankan ulang.
2. **Jangan pakai superlatif** ("selalu", "100%", "terbukti"). Pakai angka + n.
3. Deck v1 pernah memuat "91.3% / 640ms" tanpa sumber — PRD §9 sudah memperingatkan. Jangan terulang.
4. `fictional_term` = **100% (10 comply / 0 pushback / 2 error, n=12 valid)**. Angka 67% di log lama salah: ERROR dihitung sebagai PUSHBACK. Jangan pakai 67%/90%.
5. Klasifikasi memakai regex heuristik yang transparan, bukan LLM judge — itu disengaja supaya pengukurannya tidak sirkular. Sebut ini kalau juri menanyakan metodologi.

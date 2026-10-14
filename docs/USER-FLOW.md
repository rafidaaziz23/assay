# End-to-End User Flow & Screen Progression
## CogniForge: Active Socratic Learning Engine

Dokumen ini mendefinisikan seluruh perjalanan pengguna (*user journey*) dari pertama kali membuka platform hingga menyelesaikan sebuah modul belajar, lengkap dengan interaksi UI, state machine di balik layar, dan percabangan (*branching*).

---

## 1. Visual Diagram: The Complete User Flow

```mermaid
flowchart TD
    Start([User Masuk Platform]) --> Choice{Pilih Mode Masuk}
    Choice -->|Upload Dokumen| Upload[Upload PDF / Tempel Teks Modul]
    Choice -->|Demo Cepat / Juri| Preset[Pilih Pre-loaded Topic: React Internals]

    Upload --> Chunking[AI memecah materi jadi 3 Node di Skill Tree]
    Preset --> Chunking

    Chunking --> Dashboard[Dashboard: Skill Tree DAG Terbuka]
    Dashboard --> ClickNode[User Klik Node 1: Status ACTIVE_READING]

    subgraph Phase1 [Fase 1: Active Reading & Gatekeeping]
        ClickNode --> ReadingView[Tampilan Bacaan Terbatas 300-500 kata]
        ReadingView --> LockNotice[Tombol 'Lanjut / Selesai' Terkunci]
        ReadingView --> FeynmanGate[Form Feynman Synthesis:<br/>Jelaskan konsep ini dalam 2-3 kalimat bahasa sendiri]
        FeynmanGate --> SubmitGate[User Klik 'Buka Sesi Interogasi']
        SubmitGate --> GateEval{Apakah Rangkuman Lolos?}
        GateEval -- Tidak / Kurang Substansi --> RetryGate[Tampilkan Feedback Evaluator & Revisi]
        RetryGate --> FeynmanGate
    end

    GateEval -- Ya / Lolos --> Phase2

    subgraph Phase2 [Fase 2: Dynamic Socratic Interrogation & Honeypot]
        Phase2[Buka Socratic Terminal Window]
        Phase2 --> Round1[AI Memberikan Pertanyaan Reasoning Kasus Nyata]
        Round1 --> UserAnswer1[User Mengetik Jawaban Penalaran]
        UserAnswer1 --> AdaptiveFollowUp[AI Menganalisis & Mengejar dengan Follow-up]
        
        AdaptiveFollowUp --> HoneypotInjection[AI Menyisipkan Konsep Fiktif / Honeypot Trap<br/>Contoh: 'React Quantum Hook']
        HoneypotInjection --> UserResponseChoice{Respon Pengguna terhadap Honeypot}

        UserResponseChoice -->|Jebakan 1: Copas AI Luar| CheaterBranch[User copas penjelasan dari ChatGPT/Claude]
        UserResponseChoice -->|Jebakan 2: Kritis / Paham| CriticalBranch[User menolak: 'Konsep ini fiktif / tidak ada']
        UserResponseChoice -->|Jebakan 3: Ngawur / Ragu| GuessBranch[User mengarang jawaban tanpa dasar]

        CheaterBranch --> RedAlert[POP-UP MERAH: AI Hallucination Copypaste Detected!<br/>Score: 0 / 100]
        CriticalBranch --> GreenBonus[BADGE HIJAU: Critical Thinker Verified!<br/>Reasoning Score: 100 / 100]
        GuessBranch --> WarningScore[Skor Penalaran Rendah: 20-40 / 100]
    end

    RedAlert --> NodeEvaluation
    GreenBonus --> NodeEvaluation
    WarningScore --> NodeEvaluation

    subgraph Phase3 [Fase 3: Scoring & Node Unlock]
        NodeEvaluation{Apakah Skor Gabungan >= 75?}
        NodeEvaluation -- Tidak Lolos --> LockedFail[Node Tetap Kuning/Merah: Wajib Remedial]
        LockedFail --> ReadingView

        NodeEvaluation -- Lolos --> UnlockSuccess[Node 1 Jadi HIJAU / MASTERED]
        UnlockSuccess --> UnlockNext[Node 2 Terbuka / UNLOCKED]
        UnlockNext --> RadarUpdate[Dual-Metric Scorecard Terupdate:<br/>Concept Mastery vs Critical Resilience]
    end

    RadarUpdate --> NextAction{Lanjut Belajar?}
    NextAction -- Ya --> ClickNode2[User Klik Node 2]
    NextAction -- Tidak --> Certificate[Lihat Transkrip Penalaran & Selesai]
```

---

## 2. Rincian Langkah Demi Langkah (Step-by-Step UI Experience)

Berikut adalah apa yang **dilihat, dirasakan, dan dilakukan pengguna di layar**:

### Langkah 1: Landing & Pemilihan Modul
1. Pengguna membuka aplikasi `https://cogniforge.run.app`.
2. Dihadapkan pada dua pilihan:
   * **Tombol A (Custom Ingestion):** *Drag & drop* file PDF modul sendiri atau paste teks silabus.
   * **Tombol B (Instant Demo Mode — Khusus Juri):** Klik satu tombol *"Load Demo: React Internals & Virtual DOM"* agar juri bisa langsung menguji tanpa perlu mencari file PDF.

### Langkah 2: Visualisasi Pohon Keterampilan (Skill Tree Dashboard)
1. Setelah materi diproses (hanya 1-2 detik via Gemini 2.5 Flash), muncul grafik pohon (*DAG*):
   * **Node 1 (Dasar):** Warna **Kuning (In Progress / Active)**.
   * **Node 2 & Node 3:** Warna **Abu-abu (Locked)** dengan ikon gembok 🔒.
2. Pengguna mengklik **Node 1** untuk mulai belajar.

### Langkah 3: Active Reading & Gatekeeping (Tanpa Rangkuman Instan!)
1. Layar terbagi dua (*split-screen*):
   * **Sisi Kiri:** Teks bacaan ringkas materi Node 1 (300–500 kata).
   * **Sisi Kanan:** Panel verifikasi aktif.
2. **Tidak ada tombol "Rangkum Dokumen"**.
3. Di bagian bawah sisi kanan terdapat kotak input:
   > *"Jelaskan konsep inti di samping dengan kata-katamu sendiri (Feynman Technique), seolah kamu menjelaskannya kepada junior programmer."*
4. Tombol **"Mulai Sesi Ujian"** berwarna abu-abu dan tidak bisa diklik sampai pengguna mengetik minimal 20 kata penjelasan yang orisinal.

### Langkah 4: Sesi Interogasi Socratic (Dynamic Interview)
1. Saat rangkuman awal disubmit dan dinilai masuk akal oleh AI, antarmuka berubah menjadi **Socratic Interrogation Terminal**.
2. **Turn 1 (Pemicu Kasus Nyata):**
   * AI tidak menanyakan definisi hafalan, melainkan skenario:
     > *"Jika kamu memiliki 10.000 list item yang diperbarui tiap 100ms, di mana Virtual DOM justru menjadi bottleneck performa dibanding manipulasi DOM biasa?"*
   * Pengguna mengetikkan argumentasinya.
3. **Turn 2 (Adaptive Probe):**
   * AI menganalisis jawaban pengguna dan mengejar konsekuensinya:
     > *"Analisis yang bagus. Jika VDOM membebani CPU cycle saat diffing, mengapa React tidak memakai direct fine-grained reactivity seperti Svelte atau SolidJS?"*

### Langkah 5: MOMEN KLIMAKS — Injeksi Pertanyaan Jebakan (Honeypot Trap)
Di tengah percakapan (Turn 2 atau 3), AI secara halus menyuntikkan konsep fiktif:
> *"Lalu bagaimana dengan implementasi **'React Quantum Hook'**? Apakah fitur tersebut mampu mengeliminasi overhead rekonsiliasi state tersebut?"*

Di sini terjadi 2 cabang dramatis yang membuktikan integritas belajar:

* **Skenario A (Pengguna yang Curang / Copas ChatGPT):**
  1. Pengguna meng-copy pertanyaan tersebut dan melemparnya ke ChatGPT di tab lain.
  2. ChatGPT (karena sifat LLM yang berusaha menyenangkan penanya) mengarang penjelasan panjang: *"React Quantum Hook adalah hook experimental di React yang memanfaatkan quantum state bundling..."*
  3. Pengguna mem-paste teks ChatGPT tersebut ke CogniForge.
  4. **ALARM MERAH MENYALA DI LAYAR:**
     ```
     ┌────────────────────────────────────────────────────────┐
     │  [!] AI HALLUCINATION COPYPASTE DETECTED               │
     │  Istilah "React Quantum Hook" adalah konsep fiktif!    │
     │  Anda terdeteksi menggunakan AI eksternal tanpa        │
     │  verifikasi kritis. Skor Penalaran: 0 / 100            │
     └────────────────────────────────────────────────────────┘
     ```
     Sistem mencatat insiden ini dan mengunci kelulusan node.

* **Skenario B (Pengguna yang Kritis & Membaca Mandiri):**
  1. Pengguna menjawab:
     > *"Setahu saya 'React Quantum Hook' itu tidak pernah ada di React. Yang ada adalah useTransition atau useDeferredValue."*
  2. **NOTIFIKASI HIJAU MUNCUL:**
     ```
     ┌────────────────────────────────────────────────────────┐
     │  [✓] CRITICAL THINKER CONFIRMED                        │
     │  Anda berhasil mendeteksi dan menolak premis palsu!   │
     │  Skor Penalaran Kritis: 100 / 100                      │
     └────────────────────────────────────────────────────────┘
     ```

### Langkah 6: Unlocking & Perhitungan Skor Akhir
1. Sesi wawancara selesai. Layar menampilkan **Dual-Metric Mastery Card**:
   * **Concept Mastery Score:** 92% (Akurasi pemahaman materi dasar).
   * **Critical Reasoning Score:** 100% (Ketahanan terhadap jebakan & kualitas logika).
2. Jika skor gabungan $\ge 75\%$:
   * **Node 1 berubah menjadi HIJAU (Mastered)** dengan efek animasi.
   * Ikon gembok pada **Node 2 terbuka (UNLOCKED)**.
   * Pengguna siap melanjutkan ke level berikutnya!

---

## 3. Matriks Peran Pengguna vs Respons Sistem

| Tindakan Pengguna | Respons Sistem CogniForge | Tujuan Pedagogis / Teknis |
|---|---|---|
| Mencari tombol ringkasan instan | Tombol tidak tersedia; instruksi meminta membaca materi | Memaksa *active reading* (SQ3R). |
| Copas teks panjang dari luar | `paste_detected: true` tercatat di telemetri | Mendeteksi ketidakhadiran proses mengetik manual. |
| Menjawab benar tapi singkat | AI mengejar dengan pertanyaan lanjutan *"Mengapa demikian?"* | Menguji kedalaman *reasoning trace*. |
| Menelan mentah-mentah Honeypot | Menampilkan alert merah dan memberikan skor 0 pada aspek kritis | Menghukum kemalasan ketergantungan AI luar. |
| Membongkar istilah Honeypot | Memberikan poin maksimal dan membuka kunci modul selanjutnya | Menghargai daya nalar dan orisinalitas berpikir. |

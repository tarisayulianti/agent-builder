# Agent Calling Agent Builder — Rencana

**Status:** DRAFT — menunggu acceptance
**Dibuat:** 2026-09-27
**Lokasi artefak:** `F:/AI-AGENT/agent-builder/PLAN.md` (setelah dibuat)

---

## 1. Goals (Goals)

Dengan sistem ini, user dapat:

1. **Trigger via chat**: Memberikan instruksi lewat chat → sistem otomatis memulai pipeline.
2. **Agent 1 (Orchestrator/CEO)**: Instance Hermes yang berperan sebagai perencana, reviewer, dan pengambil keputusan arah kerja. Bertugas:
   - Menerima instruksi awal dari user.
   - Memecah tugas menjadi sub-tugas yang dikirim ke Agent 2.
   - Memreview hasil eksekusi Agent 2.
   - Memberikan instruksi berikutnya berdasarkan hasil review.
3. **Agent 2 (Executor)**: Instance Hermes CLI yang dieksekusi via `hermes chat -q` atau tmux, bertugas:
   - Mengeksekusi kode / implementasi sesuai instruksi dari Agent 1.
   - Melaporkan hasil eksekusi kembali ke Agent 1.
4. **Loop berkelanjutan**: Setiap siklus: plan → execute → review → plan berikutnya. Berhenti saat user memberi sinyal stop atau tujuan tercapai.

---

## 2. Non-Goals (Non-Goals)

- **Tidak terkait project lain** — ini sistem standalone, terpisah dari VUA-Trading-Agent dan project lainnya.
- **Tidak include UI/dashboard** — ini CLI-first, tanpa antarmuka grafis.
- **Tidak perlu koneksi eksternal** — semua berjalan lokal via Hermes yang sudah terinstall.
- **Tidak auto-start tanpa trigger** — user harus memulai via chat atau command.
- **Tidak menggantikan agent lain yang sudah ada** — ini merupakan instance baru yang berperan sebagai orchestrator.

---

## 3. Assumptions

1. **Hermes sudah terinstall** dan terkonfigurasi di system user (model, provider, auth sudah siap).
2. **User memiliki satu sesi chat aktif** yang bisa berperan sebagai Agent 1 (orchestrator).
3. **Agent 2 di-spawn sebagai proses terpisah** — via `hermes chat -q` (one-shot) atau tmux (interaktif).
4. **`delegate_task` mencukupi** untuk komunikasi Agent 1 → Agent 2 dan menerima hasil balik.
5. **Semua berjalan di mesin yang sama** — tanpa perlu SSH, jaringan, atau environment remote.
6. **Output Agent 2 cukup informatif** untuk Agent 1 review — Agent 2 harus diminta untuk melaporkan hasil yang terstruktur.

---

## 4. Arsitektur Singkat

```
┌─────────────────────────────────────────────────────┐
│                  User (Chat Trigger)                 │
└──────────────────────┬──────────────────────────────┘
                       │ instruksi awal
                       ▼
┌─────────────────────────────────────────────────────┐
│           Agent 1 — Orchestrator/CEO                 │
│  (instance Hermes utama, planner + reviewer)         │
│                                                      │
│  1. Terima instruksi user                            │
│  2. Pecah jadi sub-tugas                            │
│  3. delegate_task → Agent 2                          │
│  4. Terima hasil balik (via delegate_task result)    │
│  5. Review → putuskan: lanjut / revisi / selesai    │
│  6. Ulang langkah 2-5 sampai tujuan tercapai        │
└──────────────────────┬──────────────────────────────┘
                       │ delegate_task (task + instruksi)
                       ▼
┌─────────────────────────────────────────────────────┐
│           Agent 2 — Executor (Worker)                │
│  (hermes chat -q / tmux spawn, proses terpisah)     │
│                                                      │
│  1. Terima task dari Agent 1                         │
│  2. Eksekusi kode / implementasi                     │
│  3. Siapkan laporan hasil (terstruktur)              │
│  4. Kembalikan ke Agent 1 via delegate_task result   │
└─────────────────────────────────────────────────────┘
```

---

## 5. Alur Kerja (Workflow)

### 5.1 Trigger (User → Agent 1)

User mengirim pesan ke Agent 1 (chat atau command):
```
> Bangun fitur X untuk project Y
> Review kode di folder Z
> Optimasi performa A
```

### 5.2 Perencanaan (Agent 1 internal)

Agent 1:
1. Memahami tujuan dari instruksi user.
2. Mengembangkan rencana / roadmap singkat (birthdot/struktur/blueprint).
3. Membagi menjadi sub-tugas yang bisa ditangani Agent 2.

### 5.3 Delegasi ke Agent 2

Agent 1 menggunakan `delegate_task`:
- **Goal**: deskripsi sub-tugas yang jelas + instruction terbatas.
- **Context**: folder kerja, constraint, format laporan yang diharapkan.
- Agent 2 di-spawn sebagai Hermes CLI instance baru.

### 5.4 Eksekusi (Agent 2)

Agent 2:
1. Membaca task + instruction.
2. Mengeksekusi kerja (coding, testing, dll).
3. Menyusun laporan hasil: apa yang dikerjakan, hasilnya, masalah yang ditemukan, saran berikutnya.

### 5.5 Report Back (Agent 2 → Agent 1)

Hasil Agent 2 masuk ke Agent 1 via `delegate_task` result. Agent 1 membaca dan mem-review.

### 5.6 Review & Decision (Agent 1)

Agent 1 memutuskan:
- ✅ **Accept**: Tugas selesai, lanjut ke sub-tugas berikutnya atau ke tujuan berikutnya.
- 🔄 **Revise**: Perlu perbaikan — kirim ulang ke Agent 2 dengan instruksi koreksi.
- 🛑 **Selesai**: Tujuan tercapai — beri summary ke user.

### 5.7 Loop Berikutnya

Agent 1 membuat instruksi berikutnya untuk Agent 2 (sub-tugas berikutnya atau koreksi), ulang dari langkah 5.3.

---

## 6. Bentuk Laporan Agent 2

Agar Agent 1 bisa review dengan efektif, Agent 2 diinstruksikan melaporkan dalam format terstruktur:

```markdown
## Laporan Eksekusi Agent 2

**Task ID**: <identifier>
**Duration**: <estimasi/waktu>

### Apa yang dilakukan
<deskripsi kerja>

### Hasil
- <hasil 1>
- <hasil 2>

### File yang diubah/dibuat
- <path/file>: <deskripsi perubahan>

### Masalah / Blocker
- <jika ada>

### Saran berikutnya (ke Agent 1)
- <saran>
```

---

## 7. Kelebihan Pendekatan Ini

- **Single Hermes instance sebagai otak** — Agent 1 menjaga konteks dan konsistensi perencanaan.
- **Agent 2 bersifat disposable** — bisa di-spawn ulang, di-kill, atau diganti instance baru tiap tugas.
- **Tidak perlu infrastruktur tambahan** — semua memanfaatkan Hermes yang sudah ada.
- **Komunikasi via delegate_task** — sudah terintegrasi di Hermes, tidak perlu mekanisme custom.
- **User tetap di loop** — Agent 1 bisa melaporkan progress ke user kapan saja.

---

## 8. Acceptance Criteria

Sistem dianggap siap saat:

1. ✅ User bisa trigger pipeline lewat chat ke Agent 1.
2. ✅ Agent 1 berhasil me-plan dan mengirim task ke Agent 2 via `delegate_task`.
3. ✅ Agent 2 (Hermes CLI) menerima task, mengeksekusi, dan mengembalikan laporan terstruktur.
4. ✅ Agent 1 menerima laporan, mem-review, dan memutuskan langkah berikutnya.
5. ✅ Loop dapat berulang sesuai kebutuhan.
6. ✅ User bisa menghentikan pipeline kapan saja.

---

## 9. Verification Strategy

Setelah implementasi, verifikasi dengan:

1. **Test trigger**: Kirim instruksi ke Agent 1, pastikan Agent 1 merespon dengan perencanaan.
2. **Test delegation**: Agent 1 mengirim task kecil ke Agent 2, pastikan Agent 2 merespon.
3. **Test laporan**: Pastikan laporan Agent 2 terstruktur dan bisa dibaca Agent 1.
4. **Test loop**: Jalankan 2-3 siklus plan→execute→review, pastikan berjalan mulus.
5. **Test stop**: User memberi sinyal stop, pastikan pipeline berhenti rapi.

---

## 10. Rencana Implementasi (Outline)

Folder struktur `F:/AI-AGENT/agent-builder/`:

```
F:/AI-AGENT/agent-builder/
├── SKILL.md                # Skill orchestration (Agent 1 behavior)
├── AGENT2_INSTRUCTION.md   # Template instruction untuk Agent 2
├── EXAMPLE_CHAT_TRIGGER.md # Contoh trigger dari user
└── PLAN.md                 # Rencana ini (dokumen perencanaan)
```

### Langkah implementasi:

1. **Buat folder `F:/AI-AGENT/agent-builder/`**
2. **Tulis `SKILL.md`** — definisi perilaku Agent 1 (orchestrator):
   - Bagaimana menerima trigger
   - Bagaimana me-plan
   - Bagaimana menggunakan `delegate_task` untuk spawn Agent 2
   - Bagaimana review hasil balik
3. **Tulis `AGENT2_INSTRUCTION.md`** — template instruksi standar untuk Agent 2:
   - Format task yang dikirim
   - Format laporan yang diharapkan
   - Constraint dan ekspektasi
4. ** dokumentasi cara pakai** (CONTOH_CHAT_TRIGGER.md atauREADME)

---

## 11. Keputusan yang Perlu User Konfirmasi (Pre-Implementation)

Sebelum implementasi dimulai, user perlu memutuskan:

1. **Apakah acceptance criteria di atas sudah memadai?** Atau perlu penyesuaian?
2. **Bagaimana Agent 1 memutuskan "selesai"?** Kriteria selesai otomatis atau user-tagged?
3. **Apakah Agent 2 bisa mengakses folder project tertentu?** Atau terbatas di folder kerja masing-masing?
4. **Apakah perlu logging/sejarah** setiap siklus untuk dokumentasi?

---

## 12. Catatan Tambahan

- Skill ini **tidak akan dimuat ke catalog Hermes global** — bersifat project-specific di `F:/AI-AGENT/agent-builder/`.
- Agent 1 dan Agent 2 adalah **instance Hermes yang sama secara software**, berbeda hanya peran dan konteks.
- Pendekatan ini memanfaatkan fitur Hermes yang sudah ada (`delegate_task`, `hermes chat -q`, tmux) tanpa perlu custom infrastructure.

---

## 13. Keputusan yang Diambil (Ditandatangani)

| # | Keputusan | Nilai |
|---|---|---|
| 1 | Acceptance criteria | Sudah memadai — langsung implementasi |
| 2 | Kriteria selesai | **Otomatis** — Agent 1 memutuskan berdasarkan checklist tujuan yang ditentukan di awal |
| 3 | Akses folder Agent 2 | **Tidak** — Agent 2 bekerja di folder yang ditentukan di instruksinya, tidak perlu akses project lain |
| 4 | Logging/sejarah | **Ya** — simpan log setiap siklus di `F:/AI-AGENT/agent-builder/logs/` |

---

## 14. Rencana Implementasi (Outline)

Folder struktur `F:/AI-AGENT/agent-builder/`:

```
F:/AI-AGENT/agent-builder/
├── SKILL.md                # Skill orchestration (Agent 1 behavior)
├── AGENT2_INSTRUCTION.md   # Template instruction untuk Agent 2
├── EXAMPLE_CHAT_TRIGGER.md # Contoh trigger dari user
├── PLAN.md                 # Rencana ini (dokumen perencanaan)
└── logs/                   # Log setiap siklus (agent-builder/logs/)
```

### Langkah implementasi:

1. **Buat folder `F:/AI-AGENT/agent-builder/` dan `F:/AI-AGENT/agent-builder/logs/`**
2. **Tulis `SKILL.md`** — definisi perilaku Agent 1 (orchestrator):
   - Bagaimana menerima trigger
   - Bagaimana me-plan
   - Bagaimana menggunakan `delegate_task` untuk spawn Agent 2
   - Bagaimana review hasil balik
   - **Bagaimana memutuskan selesai secara otomatis** berdasarkan checklist tujuan
   - **Bagaimana menyimpan log setiap siklus** ke `F:/AI-AGENT/agent-builder/logs/`
3. **Tulis `AGENT2_INSTRUCTION.md`** — template instruksi standar untuk Agent 2:
   - Format task yang dikirim
   - Format laporan yang diharapkan
   - Constraint dan ekspektasi
   - **Format laporan harus terstruktur agar Agent 1 bisa review**
4. **Tulis `EXAMPLE_CHAT_TRIGGER.md`** — contoh trigger dan respons
5. **Verifikasi end-to-end**: Trigger → Plan → Delegate → Execute → Report → Review → Auto-decide selesai

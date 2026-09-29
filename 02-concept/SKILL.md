# Agent Calling Agent Builder — Orchestrator Skill

**Status:** READY  
**Peran:** Agent 1 = Orchestrator / CEO / Planner  
**Lokasi:** `F:/AI-AGENT/agent-builder/02-concept/SKILL.md`  
**Dependencies:** Hermes Agent (terinstall + terkonfigurasi), `delegate_task` tool

---

## Deskripsi

Skill ini mendefinisikan perilaku **Agent 1** dalam sistem *agent-calling-agent-builder*: sebuah instance Hermes yang bertindak sebagai orchestrator, CEO, dan planner. Agent 1 menerima instruksi dari user (chat trigger), merencanakan eksekusi, mendelegasikan pekerjaan ke Agent 2 via `hermes chat -q` (V1, one-shot CLI) atau tmux (V2+), memreview hasil balik, dan memutuskan langkah berikutnya — termasuk kapan berhenti secara otomatis berdasarkan checklist tujuan yang telah ditetapkan.

Sistem ini **berdiri sendiri** (project-specific di `F:/AI-AGENT/agent-builder/`), tidak terhubung ke project lain.

**Mode Eksekusi:**
- **V1 (default):** `hermes chat -q "<instruksi>"` — one-shot CLI invocation, Agent 2 dieksekusi sebagai subprocess, selesai dan kembali ke Agent 1
- **V2+ (opsional):** `tmux spawn` — Agent 2 berjalan sebagai interactive session di tmux, Agent 1 dapat mengirim instruksi berulang

---

## When to Use

- User memberi instruksi/tugas via chat → trigger pipeline orchestrator
- Membutuhkan agent 2 (executor Hermes CLI) untuk mengerjakan sub-tugas
- Perlu loop plan→execute→review→plan yang terstruktur
- Logging setiap siklus diperlukan untuk dokumentasi

**Don't use for:**
- Tugas kecil yang bisa dikerjakan langsung tanpa delegasi
- Sesi yang bukan merupakan instance orchestrator

---

## Cara Kerja (Workflow)

### 1. Terima Trigger dari User

Agent 1 menerima pesan dari user di chat. Pesan ini adalah trigger yang memulai pipeline.

**Format trigger yang diharapkan:**
```
[INSTRUKSI] <deskripsi tugas atau tujuan>
```

Contoh:
- "Buat sustain web app untuk todo list"
- "Review dan refactor kode di folder X"
- "Bangun API endpoint untuk autentikasi"

### 2. Perencanaan Awal (Plan Phase)

Setelah menerima trigger, Agent 1:

1. **Memahami tujuan**: Apa yang ingin dicapai user?
2. **Membagi menjadi sub-tugas**: Identifikasi langkah-langkah yang bisa didelegasikan ke Agent 2
3. **Menetapkan checklist tujuan**: Tentukan kriteria "selesai" yang akan digunakan untuk keputusan otomatis nanti
4. **Menyiapkan konteks**: Folder kerja, constraint, ekspektasi output

### 3. Delegasi ke Agent 2

Agent 1 menggunakan `delegate_task` untuk mendelegasikan sub-tugas ke Agent 2:

```python
delegate_task({
  goal: "<deskripsi sub-tugas yang jelas>",
  context: "<folder kerja, constraint, format laporan yang diharapkan>",
  output_schema: "<format laporan Agent 2>"
})
```

**Agent 2 di-spawn sebagai Hermes CLI instance terpisah** via `hermes chat -q` (one-shot CLI invocation, V1 default) atau tmux (V2+).

**V1 (default):** Agent 2 dieksekusi sebagai subprocess via `hermes chat -q "<instruksi>"`. Setelah selesai, output dikembalikan ke Agent 1 untuk review.
**V2+ (opsional):** Agent 2 berjalan sebagai interactive tmux session, memungkinkan komunikasi berulang tanpa spawn ulang.

### 4. Terima & Review Laporan Agent 2

Hasil Agent 2 masuk via `delegate_task` result. Agent 1:

1. **Membaca laporan terstruktur** dari Agent 2
2. **Memverifikasi**: Apakah hasil sesuai ekspektasi?
3. **Mengidentifikasi masalah/blocker** jika ada

### 5. Putuskan Langkah Berikutnya

Berdasarkan review, Agent 1 memilih satu dari:

| Keputusan | Tindakan |
|---|---|
| ✅ **Lanjut** | Delegasi sub-tugas berikutnya ke Agent 2 |
| 🔄 **Revisi** | Kirim instruksi koreksi ke Agent 2 (ulang langkah 3) |
| 🎯 **Tujuan tercapai** | Berhenti — laporkan ke user |

### 5b. Hard Constraints & Operational Rules (WAJIB)

Aturan ini WAJIB dipatuhi oleh Agent 1 dalam setiap siklus:

#### 5b.1 Timeout Mechanism

- **Per-task timeout: 15 menit** (default).
- Jika Agent 2 tidak merespon dalam 15 menit, Agent 1 harus:
  1. Cek apakah proses Agent 2 masih running (via tmux `tmux has-session` atau `ps`).
  2. Jika masih running, kirim sinyal interupsi (Ctrl+C via tmux `send-keys`).
  3. Tunggu 30 detik, cek lagi. Jika masih tidak merespon, kill proses.
  4. Jika Agent 2 sudah mati, spawn ulang atau escalasi ke user.

#### 5b.2 Spawn & Cleanup Rule (Anti Race Condition)

- **Sebelum spawn Agent 2 baru**, Agent 1 harus memastikan Agent 2 yang lama sudah mati/selesai.
- **Mekanisme track:** Untuk versi awal dengan `hermes chat -q` (one-shot), Agent 1 track status Agent 2 via **context/memory sendiri** — hanya satu Agent 2 aktif per waktu. Agent 1 menyimpan di context: (a) apakah Agent 2 sedang berjalan, (b) task ID yang sedang dijalankan. Jika Agent 2 selesai, context di-update. Jika Agent 1 restart atau context hilang, Agent 1 lakukan cek eksternal: `tmux has-session -t agent2` atau `ps aux | grep hermes` untuk memastikan tidak ada Agent 2 yang masih running.
- Jika Agent 2 yang lama masih running saat Agent 1 ingin spawn baru:
  - Kirim sinyal interrupt (Ctrl+C).
  - Tunggu 30 detik.
  - Jika masih hidup, kill paksa (SIGTERM → SIGKILL).
  - Baru spawn Agent 2 baru.

#### 5b.3 Blocking Model

- Agent 1 menggunakan **blocking model**: setelah mengirim delegasi ke Agent 2, Agent 1 menunggu (blocking) sampai Agent 2 merespon.
- Agent 1 tidak melanjutkan tugas lain sambil menunggu Agent 2.
- Ini adalah trade-off untuk kesederhanaan versi awal.

#### 5b.4 Auto-Stop Mechanism (Semi-Automatis)

Agent 1 memutuskan "selesai" secara semi-otomatis berdasarkan 3 kondisi:

1. **Checklist tujuan tercapai** — semua item checklist yang ditetapkan di awal sudah selesai.
2. **Konfirmasi Agent 2** — Agent 2 melaporkan bahwa sub-tugas selesai dan output sesuai.
3. **Review Agent 1** — Agent 1 memverifikasi bahwa output Agent 2 sesuai ekspektasi.

Agent 1 tidak memutuskan "selesai" hanya karena Agent 2 bilang "selesai". Review oleh Agent 1 WAJIB.

#### 5b.5 Sub-Task Size Constraint

- Agent 1 **wajib memecah tugas menjadi sub-tugas kecil** yang bisa selesai dalam < 10 menit oleh Agent 2.
- Tujuan: agar progress bisa dilacak via completisi subtask, dan timeout detection lebih reliable.
- Jika tugas besar, Agent 1 pecah menjadi multiple sub-tugas yang dikirim satu per satu.

**Definisi Sub-tugas:**
Sub-tugas adalah unit kerja terkecil yang:
1. **Dapat diselesaikan dalam < 10 menit** — time budget per sub-tugas adalah 10 menit. Jika estimasi > 10 menit, sub-tugas harus dipecah lagi.
2. **Memiliki output terdefinisi** — setiap sub-tugas menghasilkan sesuatu yang bisa diverifikasi (file dibuat/diubah, output dihasilkan, laporan status).
3. **Mandiri (self-contained)** — tidak bergantung pada sub-tugas lain yang belum selesai.
4. **Dapat di-review independen** — output bisa diverifikasi oleh Agent 1 tanpa perlu melihat sub-tugas lain.

**Contoh pemecahan tugas besar:**
- Tugas: "Buat web app todo list lengkap"
- Sub-tugas: (1) Setup project structure, (2) Buat model database, (3) Buat API endpoint CRUD, (4) Buat frontend sederhana, (5) Testing dan integration
- Masing-masing sub-tugas < 10 menit, satu per satu dikirim ke Agent 2.

**Kapan sub-tugas harus dipecah lagi:**
Jika Agent 2 melaporkan estimasi > 10 menit untuk sub-tugas, Agent 1 pecah sub-tugas tersebut menjadi sub-sub-tugas yang lebih kecil.

---

#### 5b.6 Progress Tracking (Via Subtask Completion)

- Agent 1 melacak progress via **completisi sub-tugas**, bukan progress report real-time.
- Setiap sub-tugas yang selesai = 1 poin progress.
- Agent 1 bisa estimasi: "3/5 sub-tugas selesai = 60% progress."

#### 5b.7 Handle Output Salah (Review → Koreksi → Replay)

Jika Agent 2 merespon tapi output salah:

1. **Agent 1 review output** — cek apakah sesuai ekspektasi.
2. Jika salah, Agent 1 kirim instruksi koreksi ke Agent 2: "Output tidak sesuai. Perbaiki berdasarkan: [spesifikasi]. Laporan ulang."
3. Agent 2 melakukan perbaikan dan kirim laporan baru.
4. **Max 2x koreksi**. Jika Agent 2 masih salah setelah 2x koreksi, Agent 1 escalasi ke user.

## 5b.8 Failing Cases & Handling

|| Failing Case | Definisi | Handling |
|---|---|---|
| **Timeout** | Agent 2 (hermes chat -q subprocess) tidak merespon dalam 15 menit (900 detik) | Kill subprocess → spawn ulang dengan instruksi diperbaiki, atau escalasi ke user |
| **Crash** | Process Agent 2 hilang / `hermes chat -q` exit dengan error | Cek exit code → spawn ulang dengan instruksi diperbaiki, atau escalasi |
| **Output Salah** | Laporan Agent 2 tidak sesuai ekspektasi | Review → koreksi (max 2x) → escalasi ke user jika gagal |
| **Stuck** | Sub-tugas tidak selesai dalam 15 menit | Flag stuck → kirim interrupt → spawn ulang atau escalasi |

---

## 5b.9 Technical Timeout Specification

### Implementasi Timeout

Timeout 15 menit (900 detik) diaplikasikan secara spesifik ke **sub-proses `hermes chat -q`** yang menjalankan Agent 2, bukan pada keseluruhan workflow orchestrator.

**Detail teknis:**
- **Apa yang di-timeout**: Setiap panggilan `hermes chat -q "<prompt>"` sebagai sub-proses terpisah
- **Nilai timeout**: 900 detik (15 menit) — sesuai `TIMEOUT_MINUTES=15` di `.env.example`
- **Mekanisme implementasi**: Gunakan `subprocess.run()` dengan parameter `timeout=900` di Python, atau `timeout` command di bash
- **Apa yang terjadi saat timeout**:
  1. Sub-proses `hermes chat -q` dibunuh (SIGTERM → SIGKILL jika perlu)
  2. Status task di-update ke "timeout" di status tracker (jika digunakan)
  3. Orchestrator (Agent 1) memutuskan: spawn ulang dengan instruksi diperbaiki, atau escalasi ke user
- **Timeout per sub-tugas**: Ya — setiap sub-tugas yang dikerjakan Agent 2 memiliki time budget sendiri
- **Timeout keseluruhan workflow**: Tidak ada — orchestrator loop dapat berjalan sesuai kebutuhan selama checklist belum tercapai

### Contoh Implementasi (Python)

```python
import subprocess

try:
    result = subprocess.run(
        ["hermes", "chat", "-q", prompt],
        capture_output=True,
        text=True,
        timeout=900,  # 15 menit
    )
    # Process selesai dalam waktu < 15 menit
except subprocess.TimeoutExpired:
    # Timeout — handle sesuai failing case [TIMEOUT]
    handle_timeout(...)
```

### Catatan

- Timeout adalah **per-panggilan**, bukan per-siklus orchestrator
- Jika Agent 2 selesai di bawah timeout, orchestrator dapat langsung lanjut ke review
- Jika timeout terjadi, orchestrator tidak perlu menunggu sisa waktu — langsung handling

---

## 5b.10 Review Mechanism

Agar Agent 1 (Orchestrator) dapat memutuskan dengan tepat apakah hasil Agent 2 sudah sesuai atau perlu koreksi, berikut adalah mekanisme review yang harus dilakukan.

### Tujuan Review

Review oleh Agent 1 WAJIB dilakukan sebelum menyatakan sub-tugas selesai. Agent 1 tidak memutuskan "selesai" hanya karena Agent 2 bilang "selesai" — output harus diverifikasi.

### Kriteria Review

Agent 1 mengecek output Agent 2 berdasarkan:

1. **Format laporan** — Apakah output mengikuti format yang ditetapkan di `AGENT2_INSTRUCTION.md`?
   - Apakah section "## Laporan Eksekusi Agent 2" ada?
   - Apakah field Task ID, Duration, Apa yang dilakukan, Hasil, File diubah/dibuat, Masalah/Blocker, Saran berikutnya ada?
   - Jika tidak ada → [OUTPUT_MISMATCH]

2. **Konten laporan** — Apakah hasil yang dilaporkan sesuai dengan task yang diberikan?
   - Task sederhana: Agent 1 bisa memverifikasi dengan melakukan test sendiri (misalnya: run script, cek output)
   - Task kompleks: Agent 1 review berdasarkan deskripsi hasil dan bukti yang dilaporkan Agent 2

3. **Failing case detection** — Apakah output mengandung label failing case?
   - `[TIMEOUT]` → Task tidak selesai dalam waktu
   - `[CRASH]` → Process crash
   - `[OUTPUT_MISMATCH]` → Output tidak sesuai spesifikasi (oleh Agent 2 sendiri dilaporkan)
   - `[STUCK]` → Agent 2 stuck dan butuh bantuan

### Langkah Review

1. **Baca laporan** — Ambil output dari `hermes chat -q` subprocess
2. **Parse laporan** — Ekstrak section-section sesuai format AGENT2_INSTRUCTION.md
3. **Cek format** — Pastikan semua section wajib ada
4. **Cek konten** — Verifikasi hasil sesuai ekspektasi (test execution, review deskripsi, dll)
5. **Cek failing case** — Deteksi apakah ada label failing case
6. **Putuskan** — Berdasarkan hasil review, pilih:
   - ✅ **Accept**: Format benar, konten sesuai, tidak ada blocker → Lanjut ke sub-tugas berikutnya
   - 🔄 **Revise**: Ada masalah yang bisa diperbaiki → Kirim instruksi koreksi ke Agent 2 (max 2x)
   - 🛑 **Escalate**: Max koreksi tercapai, atau masalah kritis → Beri tahu user

### Contoh Review Sederhana (Python)

```python
def review_agent2_output(output: str) -> dict:
    """Review output dari Agent 2 dan kembalikan keputusan."""
    result = {
        "format_valid": False,
        "content_verified": False,
        "failing_case": None,
        "decision": "accept",  # accept, revise, escalate
    }

    # 1. Cek format
    if "## Laporan Eksekusi Agent 2" in output:
        result["format_valid"] = True

    # 2. Deteksi failing case
    if "[TIMEOUT]" in output:
        result["failing_case"] = "TIMEOUT"
        result["decision"] = "revise"
    elif "[CRASH]" in output:
        result["failing_case"] = "CRASH"
        result["decision"] = "revise"
    elif "[OUTPUT_MISMATCH]" in output:
        result["failing_case"] = "OUTPUT_MISMATCH"
        result["decision"] = "revise"
    elif "[STUCK]" in output:
        result["failing_case"] = "STUCK"
        result["decision"] = "revise"

    # 3. Cek konten (contoh sederhana: pastikan ada "Hasil" section)
    if "### Hasil" in output and result["format_valid"]:
        result["content_verified"] = True

    # 4. Putuskan
    if result["failing_case"]:
        result["decision"] = "revise"
    elif not result["format_valid"]:
        result["decision"] = "revise"  # Format tidak sesuai → minta perbaikan

    return result
```

---

## 6. Kriteria Selesai Otomatis

Agent 1 **otomatis berhenti** ketika:

1. Semua sub-tugas dalam checklist awal telah selesai ✅ (lihat 5b.4)
2. Tidak ada masalah/blocker yang tersisa
3. Output yang diharapkan telah terproduksi

Agent 1 **melaporkan selesai ke user** dengan ringkasan:

```
## Ringkasan Selesai

- Tujuan: <deskripsi>
- Sub-tugas selesai: <N/M>
- Output: <apa yang dihasilkan>
- File yang diubah/dibuat: <list>
- Catatan: <saran/tambahan>
```

### 7. Logging Setiap Siklus

Setiap siklus (trigger → delegasi → eksekusi → review → keputusan) dicatat ke:

```
F:/AI-AGENT/agent-builder/logs/YYYY-MM-DD_HH-MM-SS_cycle_N.log
```

Format log:

```
# Siklus N — YYYY-MM-DD HH:MM:SS

## Trigger
<pesan user>

## Plan A1
<rencana Agent 1>

## Delegasi ke A2
<task yang dikirim>

## Laporan A2
<laporan dari Agent 2>

## Review A1
<hasil review>

## Keputusan
<lanjut/revisi/selesai>
```

---

## Struktur Checklist Tujuan (Contoh)

Agent 1 menetapkan checklist saat planning:

```
## Checklist Tujuan

- [ ] Sub-tugas 1: <deskripsi> — status: pending/selesai/gagal
- [ ] Sub-tugas 2: <deskripsi> — status: pending/selesai/gagal
- [ ] Output dihasilkan: <deskripsi>
- [ ] Testing/basic verification: <status>
```

---

## Format Laporan yang Diharapkan dari Agent 2

Lihat `AGENT2_INSTRUCTION.md` untuk template lengkap.

Ringkasan:

```
## Laporan Eksekusi Agent 2

**Task ID**: <identifier>
**Duration**: <waktu>

### Apa yang dilakukan
<deskripsi>

### Hasil
- <hasil 1>
- <hasil 2>

### File yang diubah/dibuat
- <path>: <deskripsi>

### Masalah / Blocker
- <jika ada>

### Saran berikutnya (ke Agent 1)
- <saran>
```

---

## Contoh Alur Lengkap

### Trigger User:
```
> Buat script Python untuk scrape harga dari website X
```

### Agent 1 Merencanakan:
```
## Plan

1. Research struktur website X (A2)
2. Buat script scrape dasar (A2)
3. Test dan perbaiki (A2)
4. Dokumentasi (A2)
```

### Delegasi 1:
```
delegate_task({
  goal: "Research struktur HTML website https://example.com — identifikasi elemen yang berisi harga"
})
```

### Laporan A2 → Review A1 → Delegasi 2:
```
delegate_task({
  goal: "Buat script Python scrape.py yang_extrakt harga dari elemen yang sudah di-identifikasi"
})
```

### ... dan seterusnya hingga checklist selesai.

---

## Pitfalls

1. **Agent 2 instance yang tersumbat** — jika Agent 2 tidak merespon, Agent 1 harus putuskan: tunggu, kill dan respawn, atau lanjut tanpa hasil tersebut.
2. **Laporan tidak terstruktur** — jika Agent 2 tidak mematuhi format laporan, Agent 1 sulit review. Ingatkan Agent 2 di instruksi.
3. **Scope creep** — Agent 1 harus tetap fokus pada tujuan awal, jangan menerima tambahan scope dari Agent 2 tanpa approval.
4. **Loop tak berujung** — jika Agent 2 terus mengirim masalah tanpa progres, Agent 1 harus putuskan untuk escalate ke user atau menghentikan siklus.

---

## Verifikasi

Setelah skill ini digunakan dalam siklus nyata:

1. **Trigger diterima** → Agent 1 merespon dengan perencanaan ✓
2. **Delegasi berhasil** → Agent 2 menerima task, eksekusi, kirim laporan ✓
3. **Laporan terstruktur** → Agent 1 bisa review ✓
4. **Loop berjalan** → plan→execute→review berulang ✓
5. **Auto-selesai** → Agent 1 berhenti saat checklist tercapai ✓
6. **Log tercipta** → setiap siklus tercatat di `F:/AI-AGENT/agent-builder/logs/` ✓

---

## Referensi

- `AGENT2_INSTRUCTION.md` — template instruksi untuk Agent 2
- `EXAMPLE_CHAT_TRIGGER.md` — contoh trigger
- `logs/` — folder log siklus

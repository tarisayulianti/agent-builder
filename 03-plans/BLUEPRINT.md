# Agent Calling Agent Builder — Blueprint

**Status:** FINAL  
**Dibuat:** 2026-09-27  
**Lokasi:** `F:/AI-AGENT/agent-builder/BLUEPRINT.md`

---

## 1. Ringkasan Sistem

**Agent Calling Agent Builder** adalah sistem multi-agent orchestrator yang menjalankan workflow plan→execute→review→done:

- **Agent 1 (Orchestrator/CEO/Planner)** — instance Hermes yang merencanakan, mendelegasikan, mem-review, dan memutuskan selesai/tidak
- **Agent 2 (Executor)** — instance Hermes CLI (`hermes chat -q` / tmux) yang menjalankan tugas dan melaporkan hasil

Sistem berjalan di `F:/AI-AGENT/agent-builder/` dan berdiri sendiri (tidak terhubung ke project lain).

---

## 2. Arsitektur Umum

```
User (Chat Trigger)
    │
    ▼
Agent 1 (Orchestrator/CEO/Planner)
    │
    ├── Plan → pecah jadi sub-tugas
    ├── Delegate → Agent 2 via delegate_task
    ├── Review → hasil balik dari Agent 2
    └── Putuskan → lanjut / revisi / selesai
    │
    ▼
Agent 2 (Executor)
    │
    ├── Terima task
    ├── Eksekusi kode/implementasi
    └── Laporan hasil (terstruktur)
```

### Komunikasi
- **Agent 1 → Agent 2**: `delegate_task` dengan goal, context, output_schema
- **Agent 2 → Agent 1**: `delegate_task` result (laporan terstruktur)

---

## 3. Versi & Fitur

### V1 — Single Agent 2, Sequential, Blocking

| Fitur | Keterangan |
|---|---|
| Agent 2 | Single instance, hermes chat -q |
| Model | Blocking: Agent 1 tunggu Agent 2 selesai |
| Task | Sequential: satu sub-tugas per siklus |
| Spawn | hermes chat -q (one-shot) |

**File:** SKILL.md, AGENT2_INSTRUCTION.md, EXAMPLE_CHAT_TRIGGER.md, PLAN.md

### V2 — Multi-Agent 2 Paralel, Tmux Interaktif, Non-Blocking

| Fitur | Keterangan |
|---|---|
| Agent 2 | Multiple instance, tmux + hermes chat -q |
| Model | Non-blocking: Agent 1 lanjut work sambil Agent 2 jalan |
| Task | Paralel: beberapa sub-tugas bersamaan |
| Spawn | Tmux (interaktif) + hermes chat -q |
| Tracking | Status file JSON + status_tracker.py |
| Dashboard | CLI: agent-builder status |

**File tambahan:** status_tracker.py, spawn_agent2.sh, bin/agent-builder, PLAN_V2.md

### V3 — Multi-Agent 1, Agent 2 Capability, ML, Auto-Scaling

| Fitur | Keterangan |
|---|---|
| Agent 1 | Multi-instance dengan heartbeat & takeover |
| Agent 2 | Capability-based (coding, testing, general) |
| ML | Sederhana: success rate per capability |
| Auto-scaling | Spawn Agent 2 jika queue > 3 |

**File tambahan:** PLAN_V3.md, ml/task_optimizer.py

### V4 — Integrasi Eksternal

| Fitur | Keterangan |
|---|---|
| Project Management | Jira, Trello |
| Version Control | Git integration (commit, rollback) |
| CI/CD | Jenkins, GitLab CI |
| Bahasa | Multiple: Python, JavaScript, Java, C++ |

**File tambahan:** PLAN_V4.md, pm/jira_client.py, pm/trello_client.py, cicd/jenkins_client.py, cicd/gitlab_client.py

### V5 — Web Dashboard, Real-Time, Interactive

| Fitur | Keterangan |
|---|---|
| Dashboard | Web via WebSocket |
| Real-time | Status update setiap 1 detik |
| Interactive | Assign task via web interface |

**File tambahan:** PLAN_V5.md, websocket/server.py, web/static/index.html

### V6 — Advanced ML, Prediksi, Optimasi

| Fitur | Keterangan |
|---|---|
| ML | RandomForest untuk prediksi duration |
| Prediksi | Prediksi waktu selesai berdasarkan capability, complexity, dependencies |
| Optimasi | Resource allocation berdasarkan workload & capability match |

**File tambahan:** PLAN_V6.md, ml/advanced_ml.py

### V7 — Distributed, Cloud, Containerization (Opsi Cloud)

| Fitur | Keterangan |
|---|---|
| Distributed | Agent 1 & Agent 2 bisa running di mesin berbeda via REST API |
| Cloud | Deploy ke AWS, GCP, Azure |
| Containerization | Docker, Kubernetes |

**Catatan:** V7 adalah opsi cloud deployment — Docker dan K8s digunakan untuk production environment di cloud (AWS, GCP, Azure), bukan untuk Termux. **Jika user hanya pakai Termux, skip V7.** V7 tidak bisa dan tidak perlu dijalankan di Termux.

**File tambahan:** PLAN_V7.md, api/server.py, docker/Dockerfile.agent2, docker/docker-compose.yml, k8s/deployment.yaml (semua file ini adalah opsi cloud dan tidak relevan untuk Termux)

**Status:** 🔲 Plan Ready (opsi cloud, bukan Termux)

---

## 4. Struktur Folder Lengkap

```
F:/AI-AGENT/agent-builder/
│
├── Dokumen Utama
│   ├── SKILL.md                    # Agent 1 behavior + hard constraints
│   ├── AGENT2_INSTRUCTION.md       # Agent 2 instruction + failing cases
│   ├── EXAMPLE_CHAT_TRIGGER.md     # Contoh trigger & respons
│   ├── PLAN.md                     # Perencanaan awal + keputusan
│   ├── IMPLEMENTATION_PLAN.md      # Blueprint implementasi
│   ├── BLUEPRINT.md                # Blueprint lengkap (file ini)
│   │
├── Rencana Versi
│   ├── PLAN_V2.md                  # Plan V2
│   ├── PLAN_V3.md                  # Plan V3
│   ├── PLAN_V4.md                  # Plan V4
│   ├── PLAN_V5.md                  # Plan V5
│   ├── PLAN_V6.md                  # Plan V6
│   └── PLAN_V7.md                  # Plan V7
│   │
├── Script & Tool
│   ├── status_tracker.py           # Status tracker CLI
│   ├── spawn_agent2.sh             # Tmux spawn script
│   └── bin/
│       └── agent-builder           # Dashboard CLI
│   │
├── Machine Learning
│   ├── ml/
│   │   ├── task_optimizer.py       # ML sederhana
│   │   └── advanced_ml.py          # Advanced ML model
│   │
├── Integrasi Eksternal
│   ├── pm/
│   │   ├── jira_client.py          # Jira integration
│   │   └── trello_client.py        # Trello integration
│   ├── cicd/
│   │   ├── jenkins_client.py       # Jenkins integration
│   │   └── gitlab_client.py        # GitLab CI integration
│   │
├── API & Web
│   ├── api/
│   │   └── server.py               # REST API server
│   ├── websocket/
│   │   └── server.py               # WebSocket server
│   └── web/
│       └── static/
│           └── index.html          # Web dashboard
│   │
├── Log & Status
│   └── logs/
│       ├── status/
│       │   └── agent_status.json
│       ├── queue/
│       │   └── task_queue.json
│       ├── history/
│       │   └── task_history.json
│       └── *.log
│   │
├── Container & Cloud
│   ├── docker/
│   │   ├── Dockerfile.agent2
│   │   └── docker-compose.yml
│   └── k8s/
│       └── deployment.yaml
│   │
└── Adversarial Consensus Logs
    └── logs/
        ├── 2026-09-27_adversarial_r1_findings.md
        ├── 2026-09-27_adversarial_r2_crossattack.md
        ├── 2026-09-27_adversarial_r3_defend.md
        └── 2026-09-27_adversarial_distilled_bundle.md
```

---

## 5. Alur Kerja (Workflow)

### Trigger
User mengirim pesan ke Agent 1:
```
[INSTRUKSI] <deskripsi tugas>
```

### Plan (Agent 1)
1. Memahami tujuan
2. Membagi menjadi sub-tugas
3. Menetapkan checklist tujuan
4. Menyiapkan konteks

### Delegate (Agent 1 → Agent 2)
```python
delegate_task({
  goal: "<deskripsi sub-tugas>",
  context: "<folder kerja, constraint>",
  output_schema: "<format laporan>"
})
```

### Execute (Agent 2)
1. Terima task
2. Eksekusi kode/implementasi
3. Siapkan laporan terstruktur

### Report (Agent 2 → Agent 1)
Laporan terstruktur sesuai AGENT2_INSTRUCTION.md:
```markdown
## Laporan Eksekusi Agent 2

**Task ID**: <task-id>
**Duration**: <waktu>

### Apa yang dilakukan
<deskripsi>

### Hasil
- <hasil 1>
- <hasil 2>

### File yang diubah/dibuat
- `<path>`: <deskripsi>

### Masalah / Blocker
- <jika ada>

### Saran berikutnya (ke Agent 1)
- <saran>
```

### Review & Putuskan (Agent 1)
- ✅ Lanjut → delegasi sub-tugas berikutnya
- 🔄 Revisi → kirim koreksi ke Agent 2
- 🎯 Selesai → laporkan ke user

### Logging
Setiap siklus dicatat di `logs/YYYY-MM-DD_HH-MM-SS_cycle_N.log`

---

## 6. Hard Constraints (WAJIB)

### 6.1 Timeout Mechanism
- **Per-task timeout: 15 menit**
- Jika Agent 2 tidak merespon dalam 15 menit:
  1. Cek apakah proses Agent 2 masih running
  2. Jika masih running, kirim sinyal interupsi
  3. Tunggu 30 detik, cek lagi
  4. Jika masih tidak merespon, kill proses
  5. Spawn ulang atau escalasi ke user

### 6.2 Spawn & Cleanup Rule (Anti Race Condition)
- **Sebelum spawn Agent 2 baru**, pastikan Agent 2 yang lama sudah mati/selesai
- **Mekanisme track:** Untuk versi awal dengan `hermes chat -q`, Agent 1 track status Agent 2 via context/memory sendiri — hanya satu Agent 2 aktif per waktu. Agent 1 menyimpan di context: (a) apakah Agent 2 sedang berjalan, (b) task ID yang sedang dijalankan. Jika Agent 2 selesai, context di-update. Jika Agent 1 restart atau context hilang, Agent 1 lakukan cek eksternal: `tmux has-session -t agent2` atau `ps aux | grep hermes` untuk memastikan tidak ada Agent 2 yang masih running.
- Jika Agent 2 yang lama masih running saat Agent 1 ingin spawn baru:
  - Kirim sinyal interrupt (Ctrl+C)
  - Tunggu 30 detik
  - Jika masih hidup, kill paksa (SIGTERM → SIGKILL)
  - Baru spawn Agent 2 baru

### 6.3 Blocking Model
- Agent 1 menggunakan **blocking model**: setelah mengirim delegasi ke Agent 2, Agent 1 menunggu (blocking) sampai Agent 2 merespon.
- Agent 1 tidak melanjutkan tugas lain sambil menunggu Agent 2.
- Ini adalah trade-off untuk kesederhanaan versi awal.

### 6.4 Auto-Stop Mechanism (Semi-Automatis)
Agent 1 memutuskan "selesai" secara semi-otomatis berdasarkan 3 kondisi:
1. **Checklist tujuan tercapai** — semua item checklist yang ditetapkan di awal sudah selesai.
2. **Konfirmasi Agent 2** — Agent 2 melaporkan bahwa sub-tugas selesai dan output sesuai.
3. **Review Agent 1** — Agent 1 memverifikasi bahwa output Agent 2 sesuai ekspektasi.

Agent 1 tidak memutuskan "selesai" hanya karena Agent 2 bilang "selesai". Review oleh Agent 1 WAJIB.

### 6.5 Sub-Task Size Constraint
- Agent 1 **wajib memecah tugas menjadi sub-tugas kecil** yang bisa selesai dalam < 10 menit oleh Agent 2.
- Tujuan: agar progress bisa dilacak via completisi subtask, dan timeout detection lebih reliable.
- Jika tugas besar, Agent 1 pecah menjadi multiple sub-tugas yang dikirim satu per satu.

### 6.6 Progress Tracking (Via Subtask Completion)
- Agent 1 melacak progress via **completisi sub-tugas**, bukan progress report real-time.
- Setiap sub-tugas yang selesai = 1 poin progress.
- Agent 1 bisa estimasi: "3/5 sub-tugas selesai = 60% progress."

### 6.7 Handle Output Salah (Review → Koreksi → Replay)
Jika Agent 2 merespon tapi output salah:
1. **Agent 1 review output** — cek apakah sesuai ekspektasi.
2. Jika salah, Agent 1 kirim instruksi koreksi ke Agent 2: "Output tidak sesuai. Perbaiki berdasarkan: [spesifikasi]. Laporan ulang."
3. Agent 2 melakukan perbaikan dan kirim laporan baru.
4. **Max 2x koreksi**. Jika Agent 2 masih salah setelah 2x koreksi, Agent 1 escalasi ke user.

### 6.8 Failing Cases & Handling

| Failing Case | Definisi | Handling |
|---|---|---|
| **Timeout** | Agent 2 tidak merespon dalam 15 menit | Kirim interrupt → tunggu 30 detik → kill → spawn ulang atau escalasi |
| **Crash** | Process Agent 2 hilang / exit dengan error | Cek exit code → spawn ulang dengan instruksi diperbaiki, atau escalasi |
| **Output Salah** | Laporan Agent 2 tidak sesuai ekspektasi | Review → koreksi (max 2x) → escalasi ke user jika gagal |
| **Stuck** | Sub-tugas tidak selesai dalam 15 menit | Flag stuck → kirim interrupt → spawn ulang atau escalasi |

---

## 7. Status File Format

`F:/AI-AGENT/agent-builder/logs/status/agent_status.json`:
```json
{
  "timestamp": "2026-09-27T14:00:00Z",
  "agents": [
    {
      "id": "agent-2-1",
      "task_id": "task-001",
      "mode": "tmux",
      "status": "running",
      "start_time": "2026-09-27T14:00:00Z",
      "progress": "0%",
      "notes": "Just started"
    }
  ]
}
```

Status values: `running`, `done`, `failed`, `timeout`, `stuck`

---

## 8. Laporan Agent 2 — Format Wajib

### Laporan Sukses
```markdown
## Laporan Eksekusi Agent 2

**Task ID**: <task-id>
**Duration**: <waktu>

### Apa yang melakukan
<deskripsi>

### Hasil
- <hasil 1>

### File yang diubah/dibuat
- `<path>`: <deskripsi>

### Masalah / Blocker
Tidak ada

### Saran berikutnya (ke Agent 1)
<saran>
```

### Laporan Timeout
```markdown
### Masalah / Blocker
- [TIMEOUT] Task tidak selesai dalam 15 menit. Progress saat timeout: <progress>.
- File yang sudah dibuat: <list file>
- Sisa pekerjaan: <sisa pekerjaan>
```

### Laporan Crash
```markdown
### Masalah / Blocker
- [CRASH] Process crash dengan error: <error>
- File yang sudah dibuat sebelum crash: <list file>
- Penyebab yang diduga: <penyebab>
```

### Laporan Output Salah
```markdown
### Masalah / Blocker
- [OUTPUT_MISMATCH] Output tidak sesuai spesifikasi:
  - Yang diharapkan: <spesifikasi>
  - Yang dihasilkan: <hasil>
  - Perbedaan: <perbedaan>
```

### Laporan Stuck
```markdown
### Masalah / Blocker
- [STUCK] Agent 2 stuck di: <lokasi>
- Hambatan: <hambatan>
- Yang sudah dicoba: <apa yang sudah dicoba>
- Membutuhkan bantuan Agent 1: <apa yang dibutuhkan>
```

---

## 9. Acceptance Criteria Umum

Sistem dianggap siap saat:

1. ✅ User bisa trigger pipeline via chat ke Agent 1
2. ✅ Agent 1 me-plan dan mengirim task ke Agent 2 via `delegate_task`
3. ✅ Agent 2 (Hermes CLI) menerima task, mengeksekusi, dan mengembalikan laporan terstruktur
4. ✅ Agent 1 menerima laporan, mem-review, dan memutuskan lanjut/revisi/selesai
5. ✅ Loop dapat berulang sesuai kebutuhan
6. ✅ User bisa menghentikan pipeline kapan saja
7. ✅ Logging setiap siklus tersimpan di `logs/`
8. ✅ Hard constraints (timeout, cleanup, blocking, auto-stop, sub-task size, progress tracking, output handling, failing cases) terdefinisi dan dipatuhi

---

## 10. Versi & Status

| Versi | Fitur Utama | Status |
|---|---|---|
| **V1** | Single Agent 2, sequential, blocking, hermes chat -q | ✅ Final |
| **V2** | Multi-Agent 2 paralel, tmux interaktif, non-blocking, status tracker, dashboard CLI | 🔲 Plan Ready |
| **V3** | Multi-Agent 1, Agent 2 capability, ML sederhana, auto-scaling | 🔲 Plan Ready |
| **V4** | Integrasi Eksternal (Jira/Trello, Git, CI/CD, multiple bahasa) | 🔲 Plan Ready |
| **V5** | Web dashboard, real-time status, interactive task assignment | 🔲 Plan Ready |
| **V6** | Advanced ML, prediksi waktu selesai, optimasi resource allocation | 🔲 Plan Ready |
| **V7** | Distributed agent, cloud deployment, Docker/Kubernetes | 🔲 Plan Ready |

---

## 11. Referensi

- `SKILL.md` — definisi perilaku Agent 1 dan hard constraints
- `AGENT2_INSTRUCTION.md` — template instruksi dan laporan Agent 2
- `EXAMPLE_CHAT_TRIGGER.md` — contoh penggunaan
- `PLAN.md` — perencanaan awal dan keputusan
- `IMPLEMENTATION_PLAN.md` — blueprint implementasi
- `PLAN_V2.md` s/d `PLAN_V7.md` — rencana tiap versi
- `logs/` — log siklus dan adversarial consensus

---

## 12. Catatan

- Sistem ini **berdiri sendiri** di `F:/AI-AGENT/agent-builder/`, tidak terhubung ke project lain
- Agent 1 dan Agent 2 adalah **instance Hermes yang sama secara software**, berbeda hanya peran dan konteks
- Pendekatan ini memanfaatkan fitur Hermes yang sudah ada (`delegate_task`, `hermes chat -q`, tmux) tanpa perlu custom infrastructure
- Blueprint ini adalah **dokumen final** — semua versi sudah terenvision, struktur folder sudah didefinisikan, hard constraints sudah tertulis

---

**Blueprint selesai.**

Struktur lengkap:
- 12 section dokumentasi
- 7 versi (V1-V7) dengan fitur masing-masing
- Hard constraints 8 item (WAJIB)
- Format laporan Agent 2 (4 skenario: sukses, timeout, crash, output salah, stuck)
- Status file JSON format
- Alur kerja 6 langkah (trigger, plan, delegate, execute, report, review)
- Struktur folder lengkap 20+ folder/file

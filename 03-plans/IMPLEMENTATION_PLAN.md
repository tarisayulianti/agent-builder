# Agent Calling Agent Builder — Implementation Plan

**Status:** READY  
**Dibuat:** 2026-09-27  
**Lokasi:** `F:/AI-AGENT/agent-builder/03-plans/IMPLEMENTATION_PLAN.md`

---

## Ringkasan

Dokumen ini adalah **blueprint implementasi** untuk membangun sistem Agent Calling Agent Builder dari nol di Termux (Android), tanpa Docker, memanfaatkan fitur Hermes yang sudah ada.

Target: semua artefak tercantum di bawah ini tercipta dan siap pakai.

---

## Fase 1: Setup Dasar (Wajib — V1)

### 1.1 Setup Termux

```bash
pkg update && pkg upgrade -y
pkg install git python nodejs tmux curl -y
```

### 1.2 Install Hermes Agent

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes setup --model-setup --interactive
hermes doctor
```

### 1.3 Buat Struktur Folder

```bash
mkdir -p F:/AI-AGENT/agent-builder/{logs/{status,queue,history},bin,ml,pm,cicd,api,websocket,web/static,docker,k8s}
```

### 1.4 Buat File Dokumen Utama (4 file wajib V1)

| File | Konsep |
|---|---|
| `SKILL.md` | Definisi perilaku Agent 1 (Orchestrator) + 8 hard constraints |
| `AGENT2_INSTRUCTION.md` | Template instruksi + laporan Agent 2 + 4 failing cases |
| `EXAMPLE_CHAT_TRIGGER.md` | 3 contoh trigger + respons |
| `PLAN.md` | Perencanaan awal + goals, assumptions, arsitektur, acceptance criteria |

✅ **DONE** — 4 file sudah ada.

---

## Fase 2: Blueprint & Dokumentasi (Wajib)

### 2.1 Buat BLUEPRINT.md

Bluepint lengkap V1-V7 dengan:
- 12 section: ringkasan, arsitektur, versi & fitur, struktur folder, hard constraints, format laporan, alur kerja, status versi, referensi, catatan
- Struktur folder lengkap 20+ folder/file
- 8 hard constraints WAJIB
- 4 format laporan Agent 2

✅ **DONE** — `BLUEPRINT.md` sudah ada.

### 2.2 Buat IMPLEMENTATION_PLAN.md

File ini — blueprint implementasi langkah demi langkah.

✅ **DONE** — file ini dibuat saat ini.

### 2.3 Buat ARCHITECTURE_DIAGRAM.html

Diagram arsitektur visual lengkap:
- User → Agent 1 → Agent 2 loop
- Hard constraints zone
- Infrastructure & storage
- V2-V7 extensions

✅ **DONE** — `ARCHITECTURE_DIAGRAM.html` sudah ada.

---

## Fase 3: Komponen V2 (Multi-Agent Paralel, Tmux, Non-Blocking)

### 3.1 Buat `status_tracker.py`

Fitur:
- `add` — tambah agent baru (id, task_id, mode)
- `update` — update status, progress, notes
- `list` — tampilkan semua agent
- `get` — lihat detail satu agent
- Simpan ke `logs/status/agent_status.json`

### 3.2 Buat `spawn_agent2.sh`

Fitur:
- Spawn tmux session untuk Agent 2
- Parameter: agent_id, task_description
- Auto-report status via status_tracker

### 3.3 Buat `bin/agent-builder`

Dashboard CLI:
- `agent-builder status` — lihat status semua agent
- `agent-builder logs <id>` — lihat log agent
- `agent-builder kill <id>` — kill agent

### 3.4 Update SKILL.md untuk V2

Tambah section V2 di SKILL.md:
- Multi-agent paralel via tmux
- Non-blocking model
- Status tracking via status_tracker.py

---

## Fase 4: Komponen V3 (ML & Capability-Based)

### 4.1 Buat `ml/task_optimizer.py`

Fitur:
- Rekomendasikan capability terbaik berdasarkan task type
- Hitung success rate per capability dari history
- Return rekomendasi capability untuk task baru

### 4.2 Buat `ml/advanced_ml.py`

Fitur V6:
- RandomForest prediksi duration tugas
- Optimasi resource assignment

---

## Fase 5: Komponen V4 (Integrasi Eksternal)

### 5.1 Buat `pm/jira_client.py`

- CRUD issue di Jira
- Ambil task dari Jira board

### 5.2 Buat `pm/trello_client.py`

- CRUD card di Trello
- Sync Trello board dengan task queue

### 5.3 Buat `cicd/jenkins_client.py`

- Trigger Jenkins build
- Ambil status build

### 5.4 Buat `cicd/gitlab_client.py`

- Trigger GitLab pipeline
- Ambil status pipeline

---

## Fase 6: Komponen V5 (Web Dashboard & Real-Time)

### 6.1 Buat `websocket/server.py`

- WebSocket server di port 8765
- Broadcast status update ke semua klien
- Real-time dashboard

### 6.2 Buat `web/static/index.html`

- Web dashboard interaktif
- Tampilkan status semua agent
- Real-time update via WebSocket

---

## Fase 7: Komponen V6 (Advanced ML)

### 7.1 Update `ml/advanced_ml.py`

- RandomForest untuk prediksi duration
- Optimasi resource scheduling
- Learning dari task history

---

## Fase 8: Komponen V7 (Distributed & Cloud)

### 8.1 Buat `api/server.py`

- REST API server (Flask/FastAPI)
- Endpoint: /api/status, /api/agent/<id>/status, /api/task

### 8.2 Buat `docker/Dockerfile.agent2`

- Docker image untuk Agent 2
- Termux + Hermes CLI + dependensi

### 8.3 Buat `docker/docker-compose.yml`

- Docker Compose config
- Multi-container setup

### 8.4 Buat `k8s/deployment.yaml`

- Kubernetes deployment
- Service, configmap, secret

---

## Daftar Checklis Semua File

|| # | File | Path | Status |
||---|---|---|---|
||| 1 | SKILL.md | F:/AI-AGENT/agent-builder/02-concept/SKILL.md | ✅ Ada (471 baris) |
||| 2 | AGENT2_INSTRUCTION.md | F:/AI-AGENT/agent-builder/02-concept/AGENT2_INSTRUCTION.md | ✅ Ada (219 baris) |
||| 3 | EXAMPLE_CHAT_TRIGGER.md | F:/AI-AGENT/agent-builder/04-examples/EXAMPLE_CHAT_TRIGGER.md | ✅ Ada (166 baris) |
||| 4 | PLAN.md | F:/AI-AGENT/agent-builder/03-plans/PLAN.md | ✅ Ada (281 baris) |
||| 5 | BLUEPRINT.md | F:/AI-AGENT/agent-builder/03-plans/BLUEPRINT.md | ✅ Ada (475 baris) |
||| 6 | IMPLEMENTATION_PLAN.md | F:/AI-AGENT/agent-builder/03-plans/IMPLEMENTATION_PLAN.md | ✅ Ada (278+ baris, updated) |
||| 7 | ARCHITECTURE_DIAGRAM.html | F:/AI-AGENT/agent-builder/01-overview/ARCHITECTURE_DIAGRAM.html | ✅ Ada (128 baris) |
||| 8 | status_tracker.py | F:/AI-AGENT/agent-builder/status_tracker.py | ✅ Ada, berjalan, --test PASS 6/6 |
||| 9 | spawn_agent2.sh | F:/AI-AGENT/agent-builder/spawn_agent2.sh | ✅ Ada (V1: hermes chat -q) |
||| 10 | bin/agent-builder | F:/AI-AGENT/agent-builder/bin/agent-builder | ✅ Ada, semua CLI command PASS (help, status, logs, plan, run) |
||| 11 | hermes_client.py | F:/AI-AGENT/agent-builder/hermes_client.py | ✅ Ada, --help + --test PASS 4/4 |
||| 12 | orca.py | F:/AI-AGENT/agent-builder/orca.py | ✅ Ada, CLI command PASS (--help, status, logs, plan, run) |
||| 13 | logs/status/agent_status.json | F:/AI-AGENT/agent-builder/logs/status/agent_status.json | ✅ Ada |
||| 14 | logs/queue/task_queue.json | F:/AI-AGENT/agent-builder/logs/queue/task_queue.json | ✅ Ada |
||| 15 | logs/history/task_history.json | F:/AI-AGENT/agent-builder/logs/history/task_history.json | ✅ Ada |
||| 16 | .env.example | F:/AI-AGENT/agent-builder/05-configuration/.env.example | ✅ Ada (AGENT2_MODE=hermes-chat) |
||| 17 | END_TO_END_TEST.md | F:/AI-AGENT/agent-builder/06-testing/END_TO_END_TEST.md | ✅ Ada (14/14 test documented) |
||| 18 | V2_MULTI_AGENT.md | F:/AI-AGENT/agent-builder/07-v2-docs/V2_MULTI_AGENT.md | ✅ V2 dokumentasi (stub) |
||| 19 | V3_TASK_OPTIMIZER.md | F:/AI-AGENT/agent-builder/07-v2-docs/V3_TASK_OPTIMIZER.md | ✅ V3 dokumentasi (stub) |
||| 20 | V4_PM_INTEGRATION.md | F:/AI-AGENT/agent-builder/07-v2-docs/V4_PM_INTEGRATION.md | ✅ V4 dokumentasi (stub) |
||| 21 | V5_WEB_DASHBOARD.md | F:/AI-AGENT/agent-builder/07-v2-docs/V5_WEB_DASHBOARD.md | ✅ V5 dokumentasi (stub) |
||| 22 | V6_ADVANCED_ML.md | F:/AI-AGENT/agent-builder/07-v2-docs/V6_ADVANCED_ML.md | ✅ V6 dokumentasi (stub) |
||| 23 | V7_CLOUD_DEPLOYMENT.md | F:/AI-AGENT/agent-builder/07-v2-docs/V7_CLOUD_DEPLOYMENT.md | ✅ V7 dokumentasi (stub) |
||| 24 | ml/task_optimizer.py | F:/AI-AGENT/agent-builder/ml/task_optimizer.py | 🔲 V3 — Belum dibuat |
||| 25 | ml/advanced_ml.py | F:/AI-AGENT/agent-builder/ml/advanced_ml.py | 🔲 V6 — Belum dibuat |
||| 26 | pm/jira_client.py | F:/AI-AGENT/agent-builder/pm/jira_client.py | 🔲 V4 — Belum dibuat |
||| 27 | pm/trello_client.py | F:/AI-AGENT/agent-builder/pm/trello_client.py | 🔲 V4 — Belum dibuat |
||| 28 | cicd/jenkins_client.py | F:/AI-AGENT/agent-builder/cicd/jenkins_client.py | 🔲 V4 — Belum dibuat |
||| 29 | cicd/gitlab_client.py | F:/AI-AGENT/agent-builder/cicd/gitlab_client.py | 🔲 V4 — Belum dibuat |
||| 30 | api/server.py | F:/AI-AGENT/agent-builder/api/server.py | 🔲 V7 — Belum dibuat |
||| 31 | websocket/server.py | F:/AI-AGENT/agent-builder/websocket/server.py | 🔲 V5 — Belum dibuat |
||| 32 | web/static/index.html | F:/AI-AGENT/agent-builder/web/static/index.html | 🔲 V5 — Belum dibuat |
||| 33 | docker/Dockerfile.agent2 | F:/AI-AGENT/agent-builder/docker/Dockerfile.agent2 | 🔲 V7 — Belum dibuat |
||| 34 | docker/docker-compose.yml | F:/AI-AGENT/agent-builder/docker/docker-compose.yml | 🔲 V7 — Belum dibuat |
||| 35 | k8s/deployment.yaml | F:/AI-AGENT/agent-builder/k8s/deployment.yaml | 🔲 V7 — Belum dibuat |

---

## Folder Structure (Update)

Struktur folder yang ada di project:

```
agent-builder/
├── 01-overview/
│   ├── README.md
│   └── ARCHITECTURE_DIAGRAM.html
├── 02-concept/
│   ├── SKILL.md                    # Orchestrator Skill (Agent 1 behavior)
│   └── AGENT2_INSTRUCTION.md      # Agent 2 instruction template
├── 03-plans/
│   ├── PLAN.md                     # Perencanaan proyek
│   ├── BLUEPRINT.md                # Blueprint lengkap V1-V7
│   └── IMPLEMENTATION_PLAN.md      # Panduan implementasi
├── 04-examples/
│   └── EXAMPLE_CHAT_TRIGGER.md     # Contoh penggunaan
├── 05-configuration/
│   └── .env.example                # Template environment
├── 06-testing/
│   └── INTEGRATION_TEST_GUIDE.md   # Panduan testing
├── bin/
│   └── agent-builder               # CLI wrapper
├── logs/
│   ├── history/
│   │   └── task_history.json
│   ├── queue/
│   │   └── task_queue.json
│   └── status/
│       ├── agent_status.json
│       └── last_plan.json
├── status_tracker.py               # Status tracker (V1)
├── hermes_client.py                # Hermes CLI wrapper (V1)
├── orca.py                         # Orchestrator CLI (V1)
├── spawn_agent2.sh                 # Spawn Agent 2 (V1)
├── PLAN_FIX.md                      # Plan perbaikan dokumentasi
└── README.md
```

Catatan: Folder `ml/`, `pm/`, `cicd/`, `api/`, `websocket/`, `web/static/`, `docker/`, `k8s/` adalah komponen V3-V7 yang belum dibuat. V1 fokus ke komponen yang ada di atas.

---

## Prioritas Pengembangan

### Prioritas 1 — V1 (Selesai ✅)
File dokumentasi utama sudah lengkap. Sistem sudah bisa dijalankan manual via chat.

### Prioritas 2 — V2 (Dijanjikan)
Status tracker + spawn script + dashboard CLI. Ini yang bikin sistem jadi lebih terotomatisasi.

### Prioritas 3 — V3-V7 (Nanti)
ML, integrasi eksternal, web dashboard, cloud — ditunda untuk development berikutnya.

---

## Cara Menggunakan Sistem (V1 — Manual)

1. **Buka chat Hermes** di Termux
2. **Kirim trigger** ke Agent 1:
   ```
   > Buat script Python fibonacci
   ```
3. **Agent 1 merencanakan** (otomatis via SKILL.md)
4. **Agent 1 delegasi** ke Agent 2 via `delegate_task`
5. **Agent 2 eksekusi** dan laporan balik
6. **Agent 1 review** dan putuskan: lanjut/revisi/selesai
7. **Ulang** sampai tujuan tercapai

---

## Referensi

- `SKILL.md` — definisi Agent 1 behavior
- `AGENT2_INSTRUCTION.md` — template Agent 2
- `BLUEPRINT.md` — blueprint lengkap V1-V7
- `ARCHITECTURE_DIAGRAM.html` — diagram visual
- `PLAN.md` — perencanaan awal

---

**Dokumentasi lengkap tersimpan di `F:/AI-AGENT/agent-builder/`.**

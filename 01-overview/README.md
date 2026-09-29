# Agent Calling Agent Builder — Ringkasan Sistem

**Status:** FINAL  
**Dibuat:** 2026-09-27  
**Folder Dokumentasi:** `~/agent-builder-docs/` (terpisah dari project)

---

## 📋 Daftar Dokumen

| Dokumen | Deskripsi | Lokasi |
|---|---|---|
| **Ringkasan Sistem** | Gambaran umum sistem, arsitektur, komponen | `01-overview/README.md` (file ini) |
| **Diagram Arsitektur** | Visualisasi lengkap sistem V1-V7 | `01-overview/ARCHITECTURE_DIAGRAM.html` |
| **Agent 1 Skill** | Perilaku orchestrator, hard constraints, workflow | `02-concept/SKILL.md` |
| **Agent 2 Instruction** | Template instruksi & laporan Agent 2, failing cases | `02-concept/AGENT2_INSTRUCTION.md` |
| **Perencanaan Awal** | Goals, non-goals, assumptions, acceptance criteria | `03-plans/PLAN.md` |
| **Blueprint** | Blueprint lengkap V1-V7, struktur folder, hard constraints | `03-plans/BLUEPRINT.md` |
| **Implementation Plan** | Panduan implementasi step-by-step | `03-plans/IMPLEMENTATION_PLAN.md` |
| **Contoh Trigger** | 3 contoh penggunaan sistem | `04-examples/EXAMPLE_CHAT_TRIGGER.md` |
| **Konfigurasi** | Template .env untuk environment setup | `05-configuration/.env.example` |
| **Panduan Testing** | Cara menjalankan integration test | `06-testing/INTEGRATION_TEST_GUIDE.md` |

---

## 🔍 Ringkasan Sistem

**Agent Calling Agent Builder** adalah sistem multi-agent orchestrator berjalan di Termux (Android) atau Windows, tanpa Docker, berdiri sendiri.

### Komponen Utama

| Komponen | Peran |
|---|---|
| **Agent 1 (Orchestrator/CEO/Planner)** | Instance Hermes yang merencanakan, mendelegasikan ke Agent 2, mem-review hasil, dan memutuskan selanjutnya |
| **Agent 2 (Executor/Implementator)** | Instance Hermes CLI yang menjalankan tugas dan melaporkan hasil terstruktur |

### Alur Kerja

```
User (Chat Trigger)
    │
    ▼
┌─────────────────────────────────────┐
│         Agent 1 — Orchestrator       │
│  Plan → Delegate → Review → Decide  │
└────────────────┬────────────────────┘
                 │ delegate_task (blocking)
                 ▼
┌─────────────────────────────────────┐
│         Agent 2 — Executor           │
│  Execute → Report (terstruktur)      │
└────────────────┬────────────────────┘
                 │ Laporan balik
                 ▼
┌─────────────────────────────────────┐
│         Agent 1 — Review & Decide   │
│  Lanjut / Revisi / Selesai          │
└─────────────────────────────────────┘
```

### Hard Constraints (WAJIB)

1. **Timeout:** 15 menit per-task
2. **Spawn + Cleanup:** Anti race condition, cek Agent 2 lama mati sebelum spawn baru
3. **Blocking model:** Agent 1 tunggu Agent 2 selesai sebelum lanjut
4. **Auto-stop:** Berhenti hanya jika checklist tujuan tercapai + tidak ada blocker + output sesuai
5. **Sub-task size:** Pecah jadi < 10 menit per sub-tugas
6. **Progress tracking:** Via completisi sub-tugas (bukan real-time)
7. **Handle output salah:** Review → koreksi → replay (max 2x) → escalasi
8. **Failing cases:** TIMEOUT \| CRASH \| OUTPUT_MISMATCH \| STUCK

### Roadmap Versi

| Versi | Fitur | Status |
|---|---|---|
| **V1** | Dokumen + hard constraints + perencanaan | ✅ Complete |
| **V2** | Multi-agent paralel, tmux, non-blocking, dashboard CLI | 🔲 Ready (butuh tmux) |
| **V3** | ML task optimizer, capability-based | 🔲 Ready (stub) |
| **V4** | Jira, Trello, Jenkins, GitLab CI | 🔲 Ready (stub) |
| **V5** | WebSocket + Web dashboard real-time | 🔲 Ready (stub) |
| **V6** | Advanced ML (RandomForest) | 🔲 Ready (stub) |
| **V7** | REST API, Docker, Kubernetes | 🔲 Ready (stub) |

---

## 🛠️ Cara Instal (Termux)

### Prerequisites

```bash
pkg update && pkg upgrade -y
pkg install git python nodejs tmux curl -y

curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes setup --model-setup --interactive
hermes doctor
```

### Cara Pakai

**Cara 1: Manual via chat**
```bash
hermes chat
> Buat script Python fibonacci
```

**Cara 2: Pakai orchestrator context (direkomendasikan)**
```bash
hermes chat -q "$(cat ~/agent-builder-docs/02-concept/SKILL.md)"
> Buat script Python fibonacci ke-N
```

---

## 📚 Referensi

- **SKILL.md** → Definisi Agent 1 behavior & hard constraints
- **AGENT2_INSTRUCTION.md** → Template instruksi & laporan Agent 2
- **BLUEPRINT.md** → Blueprint lengkap V1-V7
- **ARCHITECTURE_DIAGRAM.html** → Diagram arsitektur visual
- **PLAN.md** → Perencanaan awal & keputusan
- **IMPLEMENTATION_PLAN.md** → Panduan implementasi
- **EXAMPLE_CHAT_TRIGGER.md** → Contoh penggunaan
- **.env.example** → Template konfigurasi

---

**Dokumentasi lengkap tersedia di folder `~/agent-builder-docs/`.**

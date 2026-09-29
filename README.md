# Agent Calling Agent Builder

Agent Calling Agent Builder — sistem multi-agent orchestrator yang berjalan di Hermes Desktop App (Windows/Termux) tanpa Docker.

## Arsitektur

- **Agent 1 (Orchestrator)**: `orca.py` — menerima task, merencanakan sub-tugas, mendelegasikan ke Agent 2, mem-review hasil, memutuskan lanjut/koreksi/escalate
- **Agent 2 (Executor)**: Hermes Agent (via `hermes chat -q`) — mengeksekusi task sesuai instruksi
- **Status Tracker**: `status_tracker.py` — tracking status, queue, history

## Versi

| Versi | Mode | Eksekusi | Status |
|---|---|---|---|
| **V1** | Sequential | `hermes chat -q` (blocking) | ✅ Selesai & tested |
| **V2** | Parallel | tmux/threading (non-blocking) | ✅ Structure complete |
| **V3** | ML Optimizer | scikit-learn | 🔲 Stub dokumentasi |
| **V4** | PM Integration | Jira, Trello | 🔲 Stub dokumentasi |
| **V5** | Web Dashboard | WebSocket/HTTP | 🔲 Stub dokumentasi |
| **V6** | Advanced ML | Adaptive, anomaly detection | 🔲 Stub dokumentasi |
| **V7** | Cloud Deploy | Docker, Kubernetes | 🔲 Stub dokumentasi |

## Instalasi

```bash
# Clone
git clone <repo-url>
cd agent-builder

# Pastikan Hermes CLI tersedia
hermes --version  # v0.21.3+
```

## Penggunaan

```bash
# V1: Sequential (default)
python orca.py plan "Buat script Python fibonacci"
python orca.py run "Buat script Python fibonacci" --verbose

# V2: Parallel (multi-agent)
python orca.py run "Buat script Python fibonacci" --mode=v2 --max-agents=3

# Status & logs
python orca.py status
python orca.py logs

# CLI wrapper
python bin/agent-builder help
python bin/agent-builder status
python bin/agent-builder plan "Test task"
python bin/agent-builder run "Test task"

# Status tracker
python status_tracker.py --test
python status_tracker.py --agents
python status_tracker.py --reset
```

## Dokumentasi

- `02-concept/SKILL.md` — Agent 1 behavior + 8 hard constraints
- `02-concept/AGENT2_INSTRUCTION.md` — Template instruksi & laporan Agent 2
- `03-plans/BLUEPRINT.md` — Blueprint V1-V7
- `03-plans/PLAN.md` — Perencanaan & keputusan
- `03-plans/IMPLEMENTATION_PLAN.md` — Checklist implementasi
- `06-testing/END_TO_END_TEST.md` — Hasil testing end-to-end
- `06-testing/INTEGRATION_TEST_GUIDE.md` — Panduan testing
- `07-v2-docs/` — Dokumentasi V2-V7

## Hard Constraints

1. Timeout 15 menit per task
2. Spawn + cleanup anti-race
3. Blocking model (V1) / Non-blocking (V2)
4. Auto-stop semi-otomatis (review max 2x → escalasi)
5. Sub-task size ≤ 10 menit
6. Progress via sub-task completion
7. Review → koreksi → replay (max 2x) → eskalasi
8. Handle 4 failing cases: TIMEOUT, CRASH, OUTPUT_MISMATCH, STUCK

## Struktur File

```
agent-builder/
├── 01-overview/          # Ringkasan sistem & arsitektur
├── 02-concept/           # SKILL.md, AGENT2_INSTRUCTION.md
├── 03-plans/             # PLAN, BLUEPRINT, IMPLEMENTATION_PLAN
├── 04-examples/          # Contoh penggunaan
├── 05-configuration/     # .env.example
├── 06-testing/           # Test docs & guides
├── 07-v2-docs/           # V2-V7 documentation
├── bin/agent-builder     # CLI wrapper
├── orca.py               # Orchestrator (Agent 1)
├── status_tracker.py     # Status tracking (V1 + V2 multi-agent)
├── hermes_client.py      # Hermes CLI wrapper (ANSI strip, --test)
├── spawn_agent2.sh       # Spawn script (V1: hermes chat -q, V2: tmux/threading)
├── spawn_agent2_inner.py # V2 inner process
├── logs/                 # Status, queue, history (JSON)
└── .gitignore
```

## Penggunaan Lanjutan

**Cara 1: Manual via chat**
```bash
hermes chat
> Buat script Python fibonacci
```

**Cara 2: Orchestrator (direkomendasikan)**
```bash
python orca.py run "Buat script Python fibonacci ke-N" --verbose
```

## Testing

```bash
# V1 component tests
python status_tracker.py --test    # 10/10 PASS
python hermes_client.py --test    # 4/4 PASS

# V1 CLI
python orca.py status
python orca.py logs
python orca.py plan "Test task"
python orca.py run "Test task"

# CLI wrapper
python bin/agent-builder status
python bin/agent-builder logs
```

## Referensi
- `SKILL.md` → Agent 1 behavior & hard constraints
- `AGENT2_INSTRUCTION.md` → Template instruksi & laporan Agent 2
- `BLUEPRINT.md` → Blueprint lengkap V1-V7
- `ARCHITECTURE_DIAGRAM.html` → Diagram arsitektur visual

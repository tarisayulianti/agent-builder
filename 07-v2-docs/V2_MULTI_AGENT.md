# V2 — Multi-Agent Parallel System

## Status: 🔲 V2 — Belum mulai (V1 sudah berjalan)

## Visi
Sistem agent-builder V2 mendukung **multiple Agent 2 paralel** yang dikoordinasikan oleh satu orchestrator (Agent 1/ORCA) menggunakan **tmux session** sebagai mekanisme eksekusi paralel, menggantikan mode `hermes chat -q` sequential V1.

## Arsitektur V2
```
V2: tmux (multi-agent paralel)
├── tmux session per agent
├── Parallel dispatch (orca.py → spawn_agent2.sh tmux)
├── Non-blocking model
├── Shared queue (task_queue.json) — multi-consumer
└── Status tracker (status_tracker.py) — multi-agent
```

## Environment Setup
```bash
# 1. Pastikan tmux terinstall
tmux -V  # minimal 3.0

# 2. Update .env
AGENT2_MODE=tmux
MAX_AGENTS=3
AGENT_TIMEOUT=900  # 15 menit

# 3. Restart orca.py dengan V2 mode
python orca.py run --mode=v2 "<task description>"
```

## Komponen V2
| Komponen | File | Status |
|---|---|---|
| Multi-agent orchestrator | `orca.py` (enhanced V2) | 🔲 |
| tmux spawn script | `spawn_agent2.sh` (V2 mode) | 🔲 |
| Shared task queue | `logs/queue/task_queue.json` (multi-consumer) | 🔲 |
| Status tracker multi-agent | `status_tracker.py` (enhanced V2) | 🔲 |
| tmux session manager | `orca.py` tmux integration | 🔲 |

## Configuration (.env)
```env
# V2 settings
AGENT2_MODE=tmux
MAX_AGENTS=3
AGENT_TIMEOUT=900
TMUX_SESSION_PREFIX=agent2
QUEUE_LOCK=redis  # or file
```

## Test Commands
```bash
# Cek tmux availability
tmux ls

# Test orca.py V2 plan
python orca.py --mode=v2 plan "Test multi-agent"

# Test orca.py V2 run (dengan tmux)
python orca.py --mode=v2 run "Test multi-agent"

# Cek status semua agent
python orca.py status --all
```

## Perbedaan V1 → V2
| Aspek | V1 (saat ini) | V2 (target) |
|---|---|---|
| Eksekusi | `hermes chat -q` sequential | tmux paralel |
| Model | Blocking | Non-blocking |
| Agent | Single Agent 2 | Multiple Agent 2 |
| Queue | Single consumer | Multi-consumer |
| Timeout | 15 menit per task | 15 menit per agent |
| Review | Semi-otomatis | Semi-otomatis (per agent) |

## Constraints V2
- Hard constraints V1 tetap berlaku (timeout, anti-race, review max 2x)
- tmux harus tersedia di environment
- Shared queue thread-safe
- Anti-race: cek tmux session lama mati sebelum spawn baru

## Migration Path (V1 → V2)
1. Pastikan tmux terinstall (`tmux -V`)
2. Update `.env` dengan `AGENT2_MODE=tmux`
3. Enhanced `orca.py` — tambahkan `--mode=v2` flag
4. Enhanced `spawn_agent2.sh` — tambahkan V2 tmux mode
5. Enhanced `status_tracker.py` — support multi-agent entries
6. Test dengan `python orca.py --mode=v2 run "Test task"`

## Integration Points
- `orca.py` ↔ `spawn_agent2.sh` (tmux session management)
- `status_tracker.py` ↔ `logs/queue/task_queue.json` (multi-consumer queue)
- `hermes_client.py` ↔ `spawn_agent2.sh` (shared query mechanism)

## Next Action
Setelah V1 stabil, lanjut ke implementasi V2.
Lihat juga: [V3 Task Optimizer](V3_TASK_OPTIMIZER.md)

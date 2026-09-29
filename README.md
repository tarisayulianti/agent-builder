# Agent Calling Agent Builder

Agent Calling Agent Builder — sistem multi-agent orchestrator yang berjalan di Hermes Desktop App (Windows/Termux) tanpa Docker.

## Overview

Sistem ini mengorkestrasi pekerjaan AI agent secara otomatis:
- **Agent 1 (Orchestrator)** — menerima task, memecah menjadi sub-tasks, mendistribusikan ke Agent 2
- **Agent 2 (Executor)** — menerima sub-task, mengeksekusi via `hermes chat -q`, mengembalikan hasil

### Modes
- **V1 (default)** — Sequential, blocking. Satu Agent 2 menjalankan satu sub-task.
- **V2** — Parallel, ThreadPoolExecutor. Multiple Agent 2 menjalankan sub-task secara bersamaan.

## Quick Start

### One-shot via script
```bash
curl -sSL https://raw.githubusercontent.com/tarisayulianti/agent-builder/master/setup.sh | bash
```

### One-shot via Hermes agent prompt
```bash
# Clone repo, activate venv, run this prompt via hermes chat
hermes chat -q
> paste prompt di bawah ini ke hermes chat -q
```

**Prompt install (copy ke hermes chat -q):**

> Kamu adalah setup engineer untuk Agent Calling Agent Builder. Ikuti langkah berikut secara berurutan, verifikasi setiap langkah berhasil sebelum lanjut, dan laporkan hasil akhir.
>
> 1. **Clone repository**  
>    ```bash
>    git clone -b master https://github.com/tarisayulianti/agent-builder.git
>    cd agent-builder
>    ```
>    Verifikasi: ada `orca.py`, `status_tracker.py`, `hermes_client.py`, `spawn_agent2.sh`, `bin/agent-builder`, `setup.sh`.
>
> 2. **Buat & aktifkan venv**  
>    ```bash
>    python3 -m venv venv
>    source venv/bin/activate
>    ```
>    Verifikasi: `which python` → `venv/bin/python`.
>
> 3. **Install dependencies**  
>    ```bash
>    pip install --upgrade pip
>    pip install -r requirements.txt
>    pip install -e .
>    ```
>    Verifikasi: semua exit code 0.
>
> 4. **Verify Hermes CLI**  
>    ```bash
>    hermes --version
>    ```
>    - Ada → lanjut. Tidak ada → hentikan, beri tahu user.
>
> 5. **Setup model** (jika belum)  
>    ```bash
>    hermes setup --model-setup --interactive
>    ```
>    Provider: **Nous Research**, model: **poolside/laguna-s-2.1:free**
>
> 6. **Run self-tests**  
>    ```bash
>    python status_tracker.py --test   # 10/10
>    python hermes_client.py --test    # 4/4
>    ```
>
> 7. **Test end-to-end**  
>    ```bash
>    python orca.py run "Buat script Python fibonacci ke-10" --verbose
>    ```
>    Verifikasi: file `fibonacci.py` terbuat, ada di `logs/history/task_history.json`.
>
> 8. **Laporan akhir**  
>    ```markdown
>    ✅ Instalasi selesai
>    - Hermes version: [version]
>    - Provider: Nous Research / poolside/laguna-s-2.1:free
>    - Tests: status_tracker 10/10, hermes_client 4/4
>    - E2E test: [PASS/FAIL]
>    - Commands:
>      ```bash
>      cd ~/agent-builder
>      source venv/bin/activate
>      python orca.py run "task" --verbose              # V1
>      python orca.py run "task" --mode=v2 --verbose   # V2
>      ```
>    ```

Setelah install, langsung pakai:
```bash
python orca.py run "Buat script Python fibonacci" --verbose
```

## Commands

### orca.py (Orchestrator CLI)

```bash
# Lihat semua commands
python orca.py --help

# Buat sub-task dari deskripsi
python orca.py plan "Rancang API untuk toko online"

# Execute task (V1 sequential)
python orca.py run "Buat script Python fibonacci"

# Execute task (V2 parallel)
python orca.py run "task desk" --mode=v2 --verbose

# Lihat status semua agent
python orca.py status

# Lihat task history & logs
python orca.py logs

# Reset semua status
python orca.py reset
```

### bin/agent-builder (Bash CLI Wrapper)

```bash
# Setara dengan orca.py tapi otomatis pakai venv python
./bin/agent-builder status
./bin/agent-builder run "Buat script Python fibonacci" --verbose
./bin/agent-builder logs
./bin/agent-builder plan "test task"
```

### status_tracker.py

```bash
python status_tracker.py --test        # Run self-tests (10/10 PASS)
python status_tracker.py --status      # Show current agent status
python status_tracker.py --reset       # Reset semua status
python status_tracker.py --log-cycle   # Log cycle stats
```

### hermes_client.py

```bash
python hermes_client.py --test         # Run self-tests (4/4 PASS)
python hermes_client.py --help         # Show documentation
```

## Architecture

```
User → orca.py (Agent 1) → spawn_agent2.sh → hermes_client.py → hermes chat -q (Agent 2)
                              ↑
                        status_tracker.py
```

### V1 Flow (Sequential)
```
1. User: orca.py run "task"
2. Agent 1: plan "task" → sub-tasks JSON
3. Agent 1: spawn Agent 2 per sub-task (sequential)
4. Agent 2: hermes chat -q "sub-task" → hasil
5. Agent 2: spawn_agent_inner.py → parse hasil → JSON
6. Agent 1: aggregate semua hasil → log
```

### V2 Flow (Parallel)
```
1. User: orca.py run "task" --mode=v2
2. Agent 1: plan "task" → sub-tasks JSON
3. Agent 1: ThreadPoolExecutor → spawn semua Agent 2 secara parallel
4. Agent 2: hermes chat -q → parse → JSON (concurrent)
5. Agent 1: aggregate semua hasil → log
```

## File Structure

```
agent-builder/
├── orca.py                     # Orchestrator CLI (Agent 1)
├── status_tracker.py           # Status tracker + self-tests
├── hermes_client.py            # Hermes chat -q wrapper (Agent 2)
├── spawn_agent2.sh             # Spawn Agent 2 script
├── spawn_agent2_inner.py       # Agent 2 inner logic + report parser
├── setup.sh                    # One-shot install script
├── bin/
│   └── agent-builder           # Bash CLI wrapper
├── logs/
│   ├── status/agent_status.json       # Agent status tracker
│   ├── queue/task_queue.json          # Task queue
│   └── history/task_history.json      # Task execution history
├── 01-overview/              # README, architecture diagram
├── 02-concept/               # SKILL.md, AGENT2_INSTRUCTION.md
├── 03-plans/                 # PLAN.md, BLUEPRINT.md, IMPLEMENTATION_PLAN.md
├── 04-examples/              # Example chat triggers
├── 05-configuration/         # .env.example, hermes config
├── 06-testing/               # END_TO_END_TEST.md, INTEGRATION_TEST_GUIDE.md
├── 07-v2-docs/               # V2-V7 documentation
│   ├── V2_MULTI_AGENT.md
│   ├── V3_TASK_OPTIMIZER.md
│   ├── V4_PM_INTEGRATION.md
│   ├── V5_WEB_DASHBOARD.md
│   ├── V6_ADVANCED_ML.md
│   └── V7_CLOUD_DEPLOYMENT.md
└── requirements.txt
```

## Testing

### Self-test (tanpa hermes)
```bash
python status_tracker.py --test     # 10/10 PASS
python hermes_client.py --test      # 4/4 PASS
```

### End-to-end (dengan hermes)
```bash
python orca.py run "Buat script Python fibonacci" --verbose
python orca.py run "task" --mode=v2 --verbose
```

### Test commands
```bash
./bin/agent-builder status
./bin/agent-builder logs
./bin/agent-builder plan "test task"
./bin/agent-builder run "test task"
```

## Prerequisites

### Hard Requirements
1. **Python 3.11+** (gunakan venv yang dikonfigurasi)
2. **Hermes CLI** terinstal & terautentikasi (`hermes setup --model-setup`)
3. **Git** untuk clone repo

### Termux (Android)
```bash
pkg install python git openssh
pip install -r requirements.txt
hermes setup --model-setup --interactive
```

### Windows
```bash
pip install -r requirements.txt
hermes setup --model-setup --interactive
```

## Configuration

Salin `.env.example` jadi `.env`:
```bash
cp 05-configuration/.env.example .env
```

Edit `.env` untuk konfigurasi:
- `AGENT2_MODE=hermes-chat` (V1 default mode)
- `AGENT2_TIMEOUT=900` (15 menit)
- `SUBTASK_MAX_TIME=600` (10 menit per sub-task)

## Logs

Log otomatis tersimpan di:
- `logs/status/agent_status.json` — status semua agent
- `logs/queue/task_queue.json` — task yang pending/running/done
- `logs/history/task_history.json` — histori semua task eksekusi

Monitor logs:
```bash
python orca.py logs
python status_tracker.py --log-cycle
```

## Hard Constraints

1. **Timeout 15 menit** per task (900 detik)
2. **Spawn + cleanup anti-race** — proses Agent 2 selalu dibersihkan setelah selesai
3. **Blocking model** (V1) / **Non-blocking** (V2)
4. **Auto-stop semi-otomatis** — review max 2x, lalu escalate
5. **Sub-task size ≤ 10 menit** per sub-task
6. **Progress via sub-task completion** — progres dilacak per sub-task selesai
7. **Review → koreksi → replay (max 2x) → eskalasi**
8. **Handle 4 failing cases**: TIMEOUT, CRASH, OUTPUT_MISMATCH, STUCK

## Troubleshooting

### Hermes CLI tidak ditemukan
```bash
which hermes
hermes --version
# Pastikan hermes terinstall & di PATH
```

### Timeout error
- Periksa `AGENT2_TIMEOUT` di `.env`
- Gunakan `--verbose` untuk lihat progress real-time

### Output Mismatch
- Hermes output harus pakai format `## Laporan Eksekusi Agent 2`
- Jika tidak, sistem akan escalate otomatis (max 2x)

## License

See LICENSE file.

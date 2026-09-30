# Agent Calling Agent Builder

Agent Calling Agent Builder — a multi-agent orchestrator system running on Hermes Desktop App (Windows/Termux) without Docker.

## Overview

This system orchestrates AI agent work automatically:
- **Agent 1 (Orchestrator)**: receives task, breaks down into sub-tasks, delegates to Agent 2
- **Agent 2 (Executor)**: receives sub-task, executes via `hermes chat -q`, returns results

### Modes
- **V1 (default)** — Sequential, blocking. One Agent 2 executes one sub-task.
- **V2** — Parallel, ThreadPoolExecutor. Multiple Agent 2 agents execute sub-tasks concurrently.

## Quick Start

### 🚀 One-Line Access (setelah install)
```powershell
# PowerShell: ketik `agent` untuk buka TUI langsung
function agent { Set-Location "C:\Users\User\Desktop\agent-builder"; .\venv\Scripts\python.exe tui.py }
```

### Desktop shortcuts
- **`agent-builder.bat`** — double-click → buka TUI langsung
- **`buka-dashboard.bat`** — double-click → buka dashboard di browser

### One-shot via script
```bash
curl -sSL https://raw.githubusercontent.com/tarisayulianti/agent-builder/master/setup.sh | bash
```

### One-shot via Hermes agent prompt
```bash
# Clone repo, activate venv, paste the prompt below into hermes chat
hermes chat -q
> paste the install prompt below
```

**Install prompt (copy to `hermes chat -q`):**

> You are a setup engineer for the Agent Calling Agent Builder system. Follow each step in order, verify success before proceeding, and provide a final report.
>
> 1. **Clone repository**
>    ```bash
>    git clone -b master https://github.com/tarisayulianti/agent-builder.git
>    cd agent-builder
>    ```
>    Verify: `orca.py`, `status_tracker.py`, `hermes_client.py`, `spawn_agent2.sh`, `bin/agent-builder`, and `setup.sh` all exist.
>
> 2. **Create & activate venv**
>    ```bash
>    python3 -m venv venv
>    source venv/bin/activate
>    ```
>    Verify: `which python` resolves to `venv/bin/python`.
>
> 3. **Install dependencies**
>    ```bash
>    pip install --upgrade pip
>    pip install -r requirements.txt
>    pip install -e .
>    ```
>    Verify: all return exit code 0.
>
> 4. **Verify Hermes CLI**
>    ```bash
>    hermes --version
>    ```
>    - If present → proceed.
>    - If not found → stop and tell the user to install Hermes CLI manually.
>
> 5. **Configure model** (if not already done)
>    ```bash
>    hermes setup --model-setup --interactive
>    ```
>    Select provider: **Nous Research**, model: **poolside/laguna-s-2.1:free**
>
> 6. **Run self-tests**
>    ```bash
>    python status_tracker.py --test   # expects 10/10
>    python hermes_client.py --test    # expects 4/4
>    ```
>
> 7. **End-to-end test**
>    ```bash
>    python orca.py run "Create a Python Fibonacci script to the 10th number" --verbose
>    ```
>    Verify: `fibonacci.py` file is created; entry appears in `logs/history/task_history.json`.
>
> 8. **Final report** (output in this format)
>    ```markdown
>    ✅ Installation complete
>    - Hermes version: [version]
>    - Provider: Nous Research / poolside/laguna-s-2.1:free
>    - Tests: status_tracker 10/10, hermes_client 4/4
>    - E2E test: [PASS/FAIL]
>    - Ready commands:
>      ```bash
>      cd ~/agent-builder
>      source venv/bin/activate
>      python orca.py run "task" --verbose              # V1 sequential
>      python orca.py run "task" --mode=v2 --verbose   # V2 parallel
>      ```
>    ```

After install, run directly:
```bash
python orca.py run "Create a Python Fibonacci script to the 10th number" --verbose
```

## Commands

### orca.py (Orchestrator CLI)

```bash
python orca.py --help                         # See all commands
python orca.py plan "Design a REST API for an online store"   # Create sub-tasks
python orca.py run "Create a Python Fibonacci script"          # V1 sequential
python orca.py run "task" --mode=v2 --verbose                  # V2 parallel
python orca.py status                        # View all agent status
python orca.py logs                          # View task history & logs
python orca.py reset                         # Reset all status
```

### bin/agent-builder (Bash CLI Wrapper)

```bash
./bin/agent-builder status
./bin/agent-builder run "Create a Python Fibonacci script" --verbose
./bin/agent-builder logs
./bin/agent-builder plan "test task"
```

### status_tracker.py

```bash
python status_tracker.py --test        # Run self-tests (10/10 PASS)
python status_tracker.py --status      # Show current agent status
python status_tracker.py --reset       # Reset all status
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
4. Agent 2: hermes chat -q "sub-task" → result
5. Agent 2: spawn_agent_inner.py → parse result → JSON
6. Agent 1: aggregate all results → log
```

### V2 Flow (Parallel)
```
1. User: orca.py run "task" --mode=v2
2. Agent 1: plan "task" → sub-tasks JSON
3. Agent 1: ThreadPoolExecutor → spawn all Agent 2 concurrently
4. Agent 2: hermes chat -q → parse → JSON (concurrent)
5. Agent 1: aggregate all results → log
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

### Self-test (without hermes)
```bash
python status_tracker.py --test     # 10/10 PASS
python hermes_client.py --test      # 4/4 PASS
```

### End-to-end (with hermes)
```bash
python orca.py run "Create a Python Fibonacci script" --verbose
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
1. **Python 3.11+** (use configured venv)
2. **Hermes CLI** installed & authenticated (`hermes setup --model-setup`)
3. **Git** for cloning repo

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

Copy `.env.example` to `.env`:
```bash
cp 05-configuration/.env.example .env
```

Edit `.env` for configuration:
- `AGENT2_MODE=hermes-chat` (V1 default mode)
- `AGENT2_TIMEOUT=900` (15 minutes)
- `SUBTASK_MAX_TIME=600` (10 minutes per sub-task)

## Logs

Logs are automatically saved to:
- `logs/status/agent_status.json` — agent status
- `logs/queue/task_queue.json` — pending/running/done tasks
- `logs/history/task_history.json` — execution history

Monitor logs:
```bash
python orca.py logs
python status_tracker.py --log-cycle
```

## TUI (Terminal User Interface)

Interactive menu — no need to remember CLI commands:

```bash
python tui.py
```

Menu:
| Key | Action |
|---|---|
| 1 | Jalankan task baru (input deskripsi) |
| 2 | Lihat status agent live |
| 3 | Lihat task history |
| 4 | Reset semua status |
| 5 | Buka dashboard |
| 6 | Jalankan self-test |
| 7 | Keluar |

## Dashboard

HTML dashboard showing agent status + task history:

```bash
# Generate HTML file
python dashboard/dashboard.py --generate
# Open: dashboard/index.html

# Serve via HTTP (port 8080) + auto-open browser
python dashboard/dashboard.py --serve --open
```

## Commands Reference

Quick CLI reference (no need to memorize long commands):

| Goal | Command |
|---|---|
| Run task | `python orca.py run "deskripsi task" --verbose` |
| Run task (parallel V2) | `python orca.py run "task" --mode=v2 --verbose` |
| Plan task | `python orca.py plan "deskripsi"` |
| Check status | `python orca.py status` |
| View logs | `python orca.py logs` |
| Self-test | `python status_tracker.py --test` |
| **TUI (interactive menu)** | `python tui.py` |
| **Dashboard (HTML)** | `python dashboard/dashboard.py --generate` |
| **Dashboard (HTTP)** | `python dashboard/dashboard.py --serve --open` |

## Hard Constraints

1. **Timeout 15 minutes** per task (900 seconds)
2. **Spawn + cleanup anti-race** — Agent 2 process always cleaned after completion
3. **Blocking model** (V1) / **Non-blocking** (V2)
4. **Auto-stop semi-automatic** — review max 2x, then escalate
5. **Sub-task size ≤ 10 minutes** per sub-task
6. **Progress via sub-task completion** — progress tracked per completed sub-task
7. **Review → correction → replay (max 2x) → escalation**
8. **Handle 4 failing cases**: TIMEOUT, CRASH, OUTPUT_MISMATCH, STUCK

## Troubleshooting

### Hermes CLI not found
```bash
which hermes
hermes --version
# Ensure hermes is installed & on PATH
```

### Timeout error
- Check `AGENT2_TIMEOUT` in `.env`
- Use `--verbose` to see real-time progress

### Output Mismatch
- Hermes output must use format `## Laporan Eksekusi Agent 2`
- If not matched, system will auto-escalate (max 2x)

## License

See LICENSE file.

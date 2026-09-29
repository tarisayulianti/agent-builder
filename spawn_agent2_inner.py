#!/usr/bin/env python3
"""
spawn_agent2_inner.py — Inner Agent 2 process (V2 parallel mode)

Digunakan oleh spawn_agent2.sh untuk:
- tmux mode: dijalankan inside tmux session
- threading mode: dijalankan sebagai background process

File ini menerima task, mengirim ke hermes CLI, dan menulis hasil ke:
- logs/status/agent_<agent_id>.json (individual agent status)
- logs/history/task_history.json (append cycle)

Usage:
    python spawn_agent2_inner.py <task_id> [agent_id] [task_description]

Example:
    python spawn_agent2_inner.py "task-001" "agent1" "Buat script fibonacci"
"""

import subprocess
import sys
import json
import os
import time
import re
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.absolute()
LOGS_DIR = PROJECT_ROOT / "logs"
STATUS_DIR = LOGS_DIR / "status"
QUEUE_DIR = LOGS_DIR / "queue"
HISTORY_DIR = LOGS_DIR / "adversarial"

# Ensure directories exist
for d in [STATUS_DIR, QUEUE_DIR, HISTORY_DIR]:
    d.mkdir(parents=True, exist_ok=True)

PYTHON = sys.executable
HERMES_CMD = "hermes"


def timestamp():
    return datetime.now().isoformat()


def load_json(path, default=None):
    """Load JSON file, return default jika file tidak ada."""
    if path is None:
        return default
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    """Save data ke JSON file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def set_agent_status(agent_id, **kwargs):
    """Update status file untuk agent tertentu."""
    status_file = STATUS_DIR / f"agent_{agent_id}.json"
    data = load_json(status_file, {"agents": {}, "timestamp": ""})

    if "agents" not in data:
        data["agents"] = {}

    agent_data = data["agents"].get(agent_id, {})

    for key, value in kwargs.items():
        agent_data[key] = value

    data["agents"][agent_id] = agent_data
    data["timestamp"] = timestamp()

    save_json(status_file, data)
    return data


def build_prompt(task_id, task_description):
    """Bangun prompt sesuai format AGENT2_INSTRUCTION.md."""
    return f"""## Task

**ID**: {task_id}
**Deskripsi**: {task_description}

**Format laporan**: Wajib ikuti template laporan Agent 2:
- Gunakan markdown
- Format: ## Laporan Eksekusi Agent 2
- Sertakan: Task ID, Duration, Apa yang dilakukan, Hasil, File yang diubah/dibuat, Masalah/Blocker, Saran berikutnya
- Jika ada masalah: gunakan label [TIMEOUT], [CRASH], [OUTPUT_MISMATCH], atau [STUCK]
- Wajib laporkan dalam format terstruktur

Laporan dalam format Agent 2 standard.
"""


def strip_ansi(text):
    """Strip ANSI escape codes dari teks."""
    clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text)
    clean = clean.replace('\r\n', '\n').replace('\r', '\n')
    return clean


def execute_hermes_query(task_id, agent_id, task_description, timeout_seconds=900):
    """
    Execute hermes chat -q query untuk Agent 2.

    Returns:
        dict dengan keys: output, exit_code, timed_out, error, duration_seconds
    """
    prompt = build_prompt(task_id, task_description)

    start_time = time.time()
    result = {
        "output": "",
        "exit_code": -1,
        "timed_out": False,
        "error": None,
        "duration_seconds": 0.0,
    }

    try:
        process = subprocess.run(
            [HERMES_CMD, "chat", "-q", prompt],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        duration = time.time() - start_time
        output = ""

        if process.stdout:
            output += process.stdout

        if process.stderr:
            output += "\n" + process.stderr

        # Strip ANSI codes
        clean_output = strip_ansi(output)

        result["output"] = clean_output.strip()
        result["exit_code"] = process.returncode
        result["duration_seconds"] = duration

        if process.returncode != 0 and process.stderr:
            result["error"] = process.stderr.strip()

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        result["timed_out"] = True
        result["duration_seconds"] = duration
        result["error"] = f"Timeout after {timeout_seconds} seconds"
        result["output"] = f"""## Laporan Eksekusi Agent 2

**Task ID**: {task_id}
**Duration**: > {timeout_seconds} detik (timeout)

### Apa yang dilakukan
Task tidak selesai dalam waktu.

### Hasil
- [TIMEOUT] Task tidak selesai dalam 15 menit.

### File yang diubah/dibuat
- Tidak ada

### Masalah / Blocker
- [TIMEOUT] Timeout setelah {timeout_seconds} detik.

### Saran berikutnya (ke Agent 1)
- Periksa progress, kirim instruksi koreksi, atau escalasi."""

    except FileNotFoundError:
        duration = time.time() - start_time
        result["error"] = f'Error: Command "{HERMES_CMD}" not found.'
        result["exit_code"] = 127
        result["duration_seconds"] = duration

    except Exception as e:
        duration = time.time() - start_time
        result["error"] = str(e)
        result["exit_code"] = 1
        result["duration_seconds"] = duration

    return result


def log_cycle(task_id, agent_id, result, task_description):
    """Log siklus ke adversarial log dan task history."""
    cycle_log = {
        "timestamp": timestamp(),
        "agent_id": agent_id,
        "task_id": task_id,
        "trigger": task_description,
        "duration_seconds": round(result["duration_seconds"], 2),
        "timed_out": result["timed_out"],
        "exit_code": result["exit_code"],
        "output_preview": result["output"][:500] if result["output"] else "",
        "error": result["error"],
    }

    # Write individual cycle log
    log_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_agent-{agent_id}_task-{task_id}.log"
    log_path = LOGS_DIR / log_filename
    with open(log_path, 'w') as f:
        f.write(json.dumps(cycle_log, indent=2, ensure_ascii=False))

    return cycle_log


def main():
    """Main entry point untuk spawn_agent2_inner.py."""
    if len(sys.argv) < 2:
        print("Usage: python spawn_agent2_inner.py <task_id> [agent_id] [task_description]")
        print("Contoh: python spawn_agent2_inner.py task-001 agent1 'Buat script fibonacci'")
        sys.exit(1)

    task_id = sys.argv[1]
    agent_id = sys.argv[2] if len(sys.argv) > 2 else f"agent-{task_id}"
    task_description = sys.argv[3] if len(sys.argv) > 3 else "No description provided"

    # Set status: running
    set_agent_status(agent_id,
        task_id=task_id,
        status="running",
        progress=0,
        started_at=timestamp(),
    )

    print(f"[spawn_agent2_inner] Agent: {agent_id}")
    print(f"[spawn_agent2_inner] Task: {task_id}")
    print(f"[spawn_agent2_inner] Deskripsi: {task_description}")
    print(f"[spawn_agent2_inner] Memulai eksekusi...")

    # Execute hermes query
    result = execute_hermes_query(task_id, agent_id, task_description)

    # Parse report (basic check for Agent 2 format)
    if "## Laporan Eksekusi Agent 2" in result["output"]:
        report_status = "completed"
        failing_case = None
    elif "[TIMEOUT]" in result["output"]:
        report_status = "failed"
        failing_case = "TIMEOUT"
    elif result["timed_out"]:
        report_status = "failed"
        failing_case = "TIMEOUT"
    elif result["exit_code"] != 0:
        report_status = "failed"
        failing_case = "OUTPUT_MISMATCH"
    else:
        report_status = "partial"
        failing_case = "OUTPUT_MISMATCH"

    # Update status
    set_agent_status(agent_id,
        status=report_status,
        progress=100 if report_status in ["completed", "failed"] else 50,
        completed_at=timestamp(),
        failing_case=failing_case,
        duration_seconds=result["duration_seconds"],
        output_preview=result["output"][:200] if result["output"] else "",
    )

    # Log cycle
    log_cycle(task_id, agent_id, result, task_description)

    print(f"[spawn_agent2_inner] Selesai: {report_status}")
    print(f"[spawn_agent2_inner] Duration: {result['duration_seconds']:.1f}s")
    print(f"[spawn_agent2_inner] Output preview: {result['output'][:100]}...")

    return result


if __name__ == "__main__":
    main()

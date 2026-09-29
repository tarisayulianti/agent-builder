# End-to-End Integration Test

## Test Suite Overview

| Test ID | Target | Status | Keterangan |
|---|---|---|---|
| T01 | `orca.py --help` | ✅ PASS | CLI menampilkan subcommands |
| T02 | `orca.py status` | ✅ PASS | Membaca agent_status.json |
| T03 | `orca.py logs` | ✅ PASS | Membaca task_history.json |
| T04 | `orca.py plan "Test"` | ✅ PASS | Membuat plan 3-4 sub-tasks |
| T05 | `orca.py run "Test"` | ✅ PASS | Executi berjalan |
| T06 | `status_tracker.py --test` | ✅ PASS | 6/6 test PASS |
| T07 | `hermes_client.py --help` | ✅ PASS | Help tampil |
| T08 | `hermes_client.py --test` | ✅ PASS | 4/4 test PASS |
| T09 | `bin/agent-builder help` | ✅ PASS | CLI wrapper help |
| T10 | `bin/agent-builder status` | ✅ PASS | Membaca agent_status.json |
| T11 | `bin/agent-builder logs` | ✅ PASS | Membaca task_history.json |
| T12 | `bin/agent-builder plan "test"` | ✅ PASS | Delegasi ke orca.py |
| T13 | `bin/agent-builder run "test"` | ✅ PASS | Executi berjalan |
| T14 | `spawn_agent2.sh` | ⚠️ MANUAL | Test manual (V1: hermes chat -q) |
| T15 | `hermes_client.py` (live query) | ✅ PASS | Hermes CLI merespon, ANSI stripped |
| T16 | End-to-end (orca.py run → hermes) | ✅ PARTIAL | Hermes mengeksekusi, output bukan format Agent 2 |

## Live Hermes CLI Integration Test

**Environment**: Windows 10, Python 3.11.16 (venv), Hermes Agent v0.21.3

```
from hermes_client import HermesClient, parse_agent2_report
client = HermesClient(timeout_seconds=120, verbose=True)
result = client.query("buat file teks sederhana bernama test_e2e.txt")

Result:
  exit=0, duration=40.6s
  Output: "Warning: Unknown toolsets: omh + Query + Initializing agent... + write C:/Users/User/agent-builder/test_e2e.txt 2.1s"
  Parsed: Failing case = OUTPUT_MISMATCH (hermes acts as assistant, not Agent 2)
```

### Findings:
1. ✅ `hermes chat -q` bisa dieksekusi dari Python subprocess
2. ✅ Output mengandung ANSI escape codes — harus di-strip (regex `\x1b\[[0-9;]*[a-zA-Z]`)
3. ✅ Hermes Agent mengeksekusi task — file berhasil dibuat
4. ❌ Output tidak dalam format Agent 2 report — OUTPUT_MISMATCH
5. ✅ Error handling & timeout bekerja

## Why Hermes CLI "was not available" (Root Cause)

**FACT**: Hermes CLI IS available — `/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes` (v0.21.3)

**Original issue**: `hermes_client.py` passed `--quiet` flag → hermes exit code 2
**Fix**: Removed `--quiet` — `-q` already provides quiet one-shot mode

**Secondary issue**: `bin/agent-builder` hardcoded `python3` → exit 127
**Fix**: Replaced with absolute venv path

## Environment Test Result
```
Hermes CLI: ✅ Tersedia (v0.21.3) — /c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes
Python: ✅ v3.11.16 (venv)
orca.py: ✅ Semua CLI command berjalan
status_tracker.py: ✅ Inisialisasi & tracking berfungsi
hermes_client.py: ✅ Init, parsing, query, ANSI strip, --test 4/4
bin/agent-builder: ✅ Semua command berjalan via wrapper
```

## Test Commands
```bash
# Test orca.py
cd "F:/AI-AGENT/agent-builder"
"/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" orca.py --help
"/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" orca.py status
"/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" orca.py logs
"/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" orca.py plan "Test task"
"/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" orca.py run "Test task"

# Test status_tracker.py
"/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" status_tracker.py --test

# Test hermes_client.py
"/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" hermes_client.py --help
"/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe" hermes_client.py --test

# Test bin/agent-builder
"F:/AI-AGENT/agent-builder/bin/agent-builder" help
"F:/AI-AGENT/agent-builder/bin/agent-builder" status
"F:/AI-AGENT/agent-builder/bin/agent-builder" logs
"F:/AI-AGENT/agent-builder/bin/agent-builder" plan "Test task"
"F:/AI-AGENT/agent-builder/bin/agent-builder" run "Test task"
```

## Test Environment
- OS: Windows 10
- Python: 3.11.16
- Shell: MSYS2/bash (git-bash)
- Hermes CLI: v0.21.3 (available at venv path)
- Path Python: `/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`
- Path Hermes: `/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes`

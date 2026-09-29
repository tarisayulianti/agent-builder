#!/usr/bin/env bash
#
# spawn_agent2.sh — Spawn Agent 2 via Hermes CLI (hermes chat -q)
#
# V1: Menggunakan hermes chat -q (one-shot CLI invocation) — BLOCKING
# V2+: Parallel mode — tmux (jika tersedia) atau Python threading
#
# Usage (V1):
#   ./spawn_agent2.sh "<task description>" [task_id]
#
# Usage (V2 parallel):
#   ./spawn_agent2.sh "<task description>" [task_id] --mode=parallel [--agent-id=N]
#
# Contoh V1:
#   ./spawn_agent2.sh "Buat script Python fibonacci" task-001
#
# Contoh V2:
#   ./spawn_agent2.sh "Buat script Python fibonacci" task-001 --mode=parallel --agent-id=1
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Warna
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ── Config ──────────────────────────────────────────────────────────
PYTHON="${PYTHON:-/c/Users/User/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe}"
HERMES_CMD="${HERMES_CMD:-hermes}"
TIMEOUT_MINUTES="${TIMEOUT_MINUTES:-15}"
TIMEOUT_SECONDS=$((TIMEOUT_MINUTES * 60))

# ── V2 Parallel Config ──────────────────────────────────────────────
MODE="single"            # single | parallel
AGENT_ID=""             # for parallel mode
MAX_AGENTS="${MAX_AGENTS:-3}"

# Parse arguments
TASK_DESC=""
TASK_ID=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode=*)
            MODE="${1#*=}"
            shift
            ;;
        --agent-id=*)
            AGENT_ID="${1#*=}"
            shift
            ;;
        --help|-h)
            MODE="help"
            shift
            ;;
        *)
            if [ -z "$TASK_DESC" ]; then
                TASK_DESC="$1"
            elif [ -z "$TASK_ID" ]; then
                TASK_ID="$1"
            fi
            shift
            ;;
    esac
done

# ── Usage ───────────────────────────────────────────────────────────
usage() {
    cat << EOF
=== spawn_agent2.sh — Spawn Agent 2 via Hermes CLI ===

V1 (Sequential/BLOCKING):
    $(basename "$0") "<task description>" [task_id]

V2 (Parallel/NON-BLOCKING):
    $(basename "$0") "<task description>" [task_id] --mode=parallel [--agent-id=N]

Arguments:
    task_description  Deskripsi task yang akan dikerjakan Agent 2
    task_id           Identifier task (opsional, auto-generated jika tidak ada)

Options:
    --mode=single     V1: hermes chat -q (blocking) [default]
    --mode=parallel   V2: parallel spawn (tmux atau threading)
    --agent-id=N      ID agent (untuk parallel mode)
    -h, --help        Tampilkan help ini

Environment:
    HERMES_CMD        Perintah hermes CLI (default: hermes)
    TIMEOUT_MINUTES   Timeout dalam menit (default: 15)
    PYTHON             Path ke Python (default: venv)
    MAX_AGENTS         Max agent paralel (V2, default: 3)

EOF
}

if [ "$MODE" = "help" ] || [ -z "$TASK_DESC" ]; then
    usage
    exit 0
fi

# Generate task ID jika tidak ada
if [ -z "$TASK_ID" ]; then
    TASK_ID="task-$(date +%s)"
fi

if [ -z "$AGENT_ID" ]; then
    AGENT_ID="$TASK_ID"
fi

# ── V1: Single mode (blocking, hermes chat -q) ──────────────────────
if [ "$MODE" = "single" ]; then
    echo -e "${BLUE}=== Spawning Agent 2 (V1: single, blocking) ===${NC}"
    echo "Task ID: $TASK_ID"
    echo "Timeout: ${TIMEOUT_MINUTES} menit (${TIMEOUT_SECONDS} detik)"
    echo "Task: $TASK_DESC"
    echo ""

    # Bangun prompt sesuai format AGENT2_INSTRUCTION.md
    PROMPT="## Task

**ID**: ${TASK_ID}
**Deskripsi**: ${TASK_DESC}

**Format laporan**: Wajib ikuti template laporan Agent 2:
- Gunakan markdown
- Format: ## Laporan Eksekusi Agent 2
- Sertakan: Task ID, Duration, Apa yang dilakukan, Hasil, File yang diubah/dibuat, Masalah/Blocker, Saran berikutnya
- Jika ada masalah: gunakan label [TIMEOUT], [CRASH], [OUTPUT_MISMATCH], atau [STUCK]
- Wajib laporkan dalam format terstruktur

Laporan dalam format Agent 2 standard."

    echo -e "${YELLOW}▶  Mengirim ke Hermes Agent...${NC}"

    OUTPUT=$($PYTHON -c "
import subprocess
import sys
import re

prompt = '''${PROMPT}'''
timeout = ${TIMEOUT_SECONDS}
hermes_cmd = '${HERMES_CMD}'

try:
    result = subprocess.run(
        [hermes_cmd, 'chat', '-q', prompt],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    output = result.stdout.strip()
    if result.stderr:
        output += '\n' + result.stderr.strip()

    # Strip ANSI escape codes
    clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', output)
    clean = clean.replace('\r\n', '\n').replace('\r', '\n')

    if clean:
        print(clean)
    sys.exit(result.returncode)
except subprocess.TimeoutExpired:
    print('''## Laporan Eksekusi Agent 2

**Task ID**: ${TASK_ID}
**Duration**: > ${TIMEOUT_SECONDS} detik (timeout)

### Apa yang dilakukan
Task tidak selesai dalam waktu.

### Hasil
- [TIMEOUT] Task tidak selesai dalam 15 menit.

### File yang diubah/dibuat
- Tidak ada

### Masalah / Blocker
- [TIMEOUT] Timeout setelah 15 menit.

### Saran berikutnya (ke Agent 1)
- Periksa progress, kirim instruksi koreksi, atau escalasi.''')
    sys.exit(1)
except FileNotFoundError:
    print(f'Error: Command \"{hermes_cmd}\" not found.', file=sys.stderr)
    sys.exit(127)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1) || {
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 124 ] || [ $EXIT_CODE -eq 1 ]; then
            echo -e "${RED}⏰  TIMEOUT${NC}"
            echo -e "${YELLOW}⏳  Timeout setelah ${TIMEOUT_MINUTES} menit${NC}"
            exit 1
        elif [ $EXIT_CODE -eq 127 ]; then
            echo -e "${RED}❌  Error: hermes command not found${NC}"
            exit 127
        else
            echo -e "${RED}❌  Error: exit code $EXIT_CODE${NC}"
            exit $EXIT_CODE
        fi
    }

    echo -e "${GREEN}✅  Agent 2 selesai${NC}"
    echo ""
    echo "--- Output ---"
    echo "$OUTPUT"
    echo "--- End Output ---"

# ── V2: Parallel mode ───────────────────────────────────────────────
elif [ "$MODE" = "parallel" ]; then
    echo -e "${BLUE}=== Spawning Agent 2 (V2: parallel) ===${NC}"
    echo "Agent ID: $AGENT_ID"
    echo "Task ID: $TASK_ID"
    echo "Mode: parallel"

    # Check if tmux is available
    if command -v tmux &> /dev/null; then
        echo "Backend: tmux"
        SESSION_NAME="agent2-${AGENT_ID}"

        # Kill existing session if exists (anti-race)
        tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

        # Spawn in tmux session
        tmux new-session -d -s "$SESSION_NAME" "$PYTHON ${PROJECT_ROOT}/spawn_agent2_inner.py ${TASK_ID} \"${TASK_DESC}\"" 2>/dev/null || {
            echo -e "${RED}❌  tmux spawn gagal, fallback ke threading${NC}"
            # Fallback to threading via Python
            $PYTHON "${PROJECT_ROOT}/spawn_agent2_inner.py" "$TASK_ID" "$AGENT_ID" "$TASK_DESC" &
        }

        echo -e "${GREEN}✅  Agent 2 spawned (V2: tmux)${NC}"
        echo "Session: $SESSION_NAME"

    elif [ -f "${PROJECT_ROOT}/spawn_agent2_inner.py" ]; then
        echo "Backend: Python threading"
        # Spawn via Python threading (background process)
        $PYTHON "${PROJECT_ROOT}/spawn_agent2_inner.py" "$TASK_ID" "$AGENT_ID" "$TASK_DESC" &

        echo -e "${GREEN}✅  Agent 2 spawned (V2: threading)${NC}"
        echo "PID: $!"
    else
        echo -e "${RED}❌  V2 parallel mode membutuhkan tmux atau spawn_agent2_inner.py${NC}"
        echo "Falling back ke V1 single mode..."
        MODE="single"
        # Recursive call in single mode
        "$0" "$TASK_DESC" "$TASK_ID" --mode=single
    fi

    echo ""
    echo "Monitor: ${PROJECT_ROOT}/bin/agent-builder status --agent-id $AGENT_ID"
    echo "Logs: ${PROJECT_ROOT}/logs/status/agent_${AGENT_ID}.json"
fi

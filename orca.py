#!/usr/bin/env python3
"""
Agent Calling Agent Builder — Orchestrator CLI (orca.py)

Status: READY
Peran: Orchestrator CLI tool yang menjalankan loop plan→delegate→review→decide
Lokasi: F:/AI-AGENT/agent-builder/orca.py
Dependencies: Python 3.11+, hermes_client.py

Tool ini adalah implementasi orchestrator (Agent 1) yang berjalan sebagai
CLI tool. Tool ini:
1. Menerima task dari user (command line)
2. Merencanakan sub-tugas (Plan Phase)
3. Mengeksekusi tiap sub-tugas lewat Hermes Agent (Delegate Phase)
4. Mem-parsing dan mem-review output (Review Phase)
5. Memutuskan lanjut/koreksi/selesai (Decide Phase)

Usage:
    python orca.py run "Buat script Python fibonacci ke-N"
    python orca.py plan "Buat script Python fibonacci ke-N"
    python orca.py status
    python orca.py logs

Documentation:
    SKILL.md — definisi Agent 1 behavior + 8 hard constraints
    AGENT2_INSTRUCTION.md — template instruksi & laporan Agent 2
    status_tracker.py — status tracker (opsional, di-integrasikan)
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

# Import Hermes Client
try:
    from hermes_client import HermesClient, QueryResult, parse_agent2_report, Agent2Report
except ImportError:
    # Fallback: coba import dari path relatif
    sys.path.insert(0, str(Path(__file__).parent))
    from hermes_client import HermesClient, QueryResult, parse_agent2_report, Agent2Report


# ============================================================================
# Konfigurasi
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent
LOGS_DIR = PROJECT_ROOT / "logs"
STATUS_FILE = PROJECT_ROOT / "logs" / "status" / "agent_status.json"
HISTORY_FILE = PROJECT_ROOT / "logs" / "history" / "task_history.json"

# Timeout: 15 menit per task (sesuai hard constraint 1)
TASK_TIMEOUT_SECONDS = 900

# Max koreksi jika output salah (sesuai hard constraint 7)
MAX_CORRECTIONS = 2

# Sub-task time budget: 10 menit (sesuai hard constraint 5)
SUB_TASK_BUDGET_SECONDS = 600


# ============================================================================
# Helper Functions
# ============================================================================

def _now_iso() -> str:
    """Return timestamp ISO 8601 sekarang."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _timestamp_log() -> str:
    """Return timestamp untuk nama file log: YYYY-MM-DD_HH-MM-SS."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def ensure_logs_dir():
    """Pastikan folder logs ada."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    (LOGS_DIR / "status").mkdir(parents=True, exist_ok=True)
    (LOGS_DIR / "queue").mkdir(parents=True, exist_ok=True)
    (LOGS_DIR / "history").mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> Any:
    """Load file JSON."""
    if not path.exists():
        if "status" in path.parts and path.name == "agent_status.json":
            return {"timestamp": _now_iso(), "agents": []}
        elif "history" in path.parts and path.name == "task_history.json":
            return {"timestamp": _now_iso(), "history": []}
        elif "queue" in path.parts and path.name == "task_queue.json":
            return {"queue": []}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure history key selalu ada
            if "history" in path.parts and path.name == "task_history.json":
                if not isinstance(data, dict) or "history" not in data:
                    return {"timestamp": _now_iso(), "history": []}
            return data
    except (json.JSONDecodeError, IOError):
        return None


def save_json(path: Path, data: Any) -> None:
    """Simpan data ke file JSON."""
    ensure_logs_dir()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log_cycle(cycle_num: int, trigger: str, plan_text: str,
              delegasi_text: str, laporan_text: str,
              review_text: str, keputusan: str):
    """Simpan log siklus ke file."""
    ensure_logs_dir()
    log_file = LOGS_DIR / f"{_timestamp_log()}_cycle_{cycle_num}.log"

    content = f"""# Siklus {cycle_num} — {_timestamp_log().replace('_', ' ')}

## Trigger
{trigger}

## Plan A1
{plan_text}

## Delegasi ke A2
{delegasi_text}

## Laporan A2
{laporan_text}

## Review A1
{review_text}

## Keputusan
{keputusan}
"""
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(content)

    # Also append to history JSON
    history_data = load_json(HISTORY_FILE) or {"timestamp": _now_iso(), "history": []}
    history_data["history"].append({
        "cycle": cycle_num,
        "timestamp": _now_iso(),
        "trigger": trigger[:200],
        "keputusan": keputusan,
    })
    save_json(HISTORY_FILE, history_data)


# ============================================================================
# Plan Phase
# ============================================================================

def plan_task(task_description: str) -> dict:
    """
    Plan Phase: pecah task menjadi sub-tugas + checklist.

    Args:
        task_description: Deskripsi task dari user

    Returns:
        dict dengan 'checklist' (list of str) dan 'sub_tasks' (list of dict)
    """
    # Buat sub-tugas umum berdasarkan pola task
    # Ini adalah heuristic sederhana — diimplementasikan sesuai pola yang
    # digambarkan di SKILL.md dan EXAMPLE_CHAT_TRIGGER.md

    sub_tasks = []
    checklist = []

    task_lower = task_description.lower()

    # Heuristic: jika membuat script/code
    if any(kw in task_lower for kw in ["buat", "buat script", "buat fungsi", "code", "program"]):
        sub_tasks.append({
            "id": "task-1",
            "description": f"Buat implementasi dasar sesuai spesifikasi: {task_description}",
            "estimated_minutes": 5,
        })
        checklist.append(f"Implementasi dasar dibuat: {task_description[:50]}...")

        sub_tasks.append({
            "id": "task-2",
            "description": "Test implementasi dengan input dasar",
            "estimated_minutes": 3,
        })
        checklist.append("Basic test/verifikasi script berjalan")

        sub_tasks.append({
            "id": "task-3",
            "description": "Handle edge case dan tambah error handling",
            "estimated_minutes": 5,
        })
        checklist.append("Handle edge case dan error handling")

        sub_tasks.append({
            "id": "task-4",
            "description": "Dokumentasi dan final review",
            "estimated_minutes": 3,
        })
        checklist.append("Dokumentasi dan final review")

    # Heuristic: jika review/refactor
    elif any(kw in task_lower for kw in ["review", "refactor", "perbaiki", "fix"]):
        sub_tasks.append({
            "id": "task-1",
            "description": f"Review kode: identifikasi issue, bug, tech debt",
            "estimated_minutes": 5,
        })
        checklist.append("Review kode selesai — issue diidentifikasi")

        sub_tasks.append({
            "id": "task-2",
            "description": "Refactor issue yang ditemukan sesuai prioritas",
            "estimated_minutes": 8,
        })
        checklist.append("Issue direfactor")

        sub_tasks.append({
            "id": "task-3",
            "description": "Verifikasi setelah refactor — test dan review ulang",
            "estimated_minutes": 5,
        })
        checklist.append("Verifikasi setelah refactor selesai")

    # Default: generic task
    else:
        sub_tasks.append({
            "id": "task-1",
            "description": f"Pelajari dan plan pendekatan untuk: {task_description}",
            "estimated_minutes": 5,
        })
        checklist.append("Pendekatan diplan")

        sub_tasks.append({
            "id": "task-2",
            "description": f"Eksekusi implementasi: {task_description}",
            "estimated_minutes": 10,
        })
        checklist.append("Implementasi selesai")

        sub_tasks.append({
            "id": "task-3",
            "description": "Test, review, dan finalisasi",
            "estimated_minutes": 5,
        })
        checklist.append("Test dan finalisasi selesai")

    return {
        "checklist": checklist,
        "sub_tasks": sub_tasks,
        "total_subtasks": len(sub_tasks),
    }


# ============================================================================
# Delegate Phase
# ============================================================================

def delegate_to_agent2(client: HermesClient, sub_task: dict,
                        task_id: str = None) -> QueryResult:
    """
    Delegate Phase: eksekusi sub-tugas lewat Hermes Agent (Agent 2).

    Args:
        client: HermesClient instance
        sub_task: dict dengan 'id' dan 'description'
        task_id: Optional custom task ID

    Returns:
        QueryResult dari Hermes Agent
    """
    return client.query_agent2(
        task_description=sub_task["description"],
        task_id=task_id or sub_task["id"],
    )


# ============================================================================
# Review Phase
# ============================================================================

def review_agent2_report(report: Agent2Report, expected_checklist: list) -> dict:
    """
    Review Phase: review laporan Agent 2 dan tentukan apakah sudah sesuai.

    Args:
        report: Agent2Report yang sudah di-parse
        expected_checklist: List checklist item yang diharapkan

    Returns:
        dict với 'status' ('accept', 'revise', 'timeout', 'crash', 'stuck'),
        'reason', dan 'blockers' (list of str)
    """
    blockers = []
    status = "accept"

    # Cek failing cases
    if report.failing_case == "TIMEOUT":
        status = "timeout"
        blockers.append(f"[TIMEOUT] Task tidak selesai dalam waktu yang dijangkau")
    elif report.failing_case == "CRASH":
        status = "crash"
        blockers.append(f"[CRASH] Process crash — error perlu diinvestigasi")
    elif report.failing_case == "OUTPUT_MISMATCH":
        status = "revise"
        blockers.append("Output tidak sesuai format yang diharapkan")
    elif report.failing_case == "STUCK":
        status = "stuck"
        blockers.append(f"[STUCK] Agent 2 tidak bisa melanjutkan")
    elif report.masalah_blocker and report.masalah_blocker.strip().lower() not in [
        "tidak ada", "", "tidak ada masalah"
    ]:
        # Ada blocker yang dilaporkan
        blockers.append(f"Blocker: {report.masalah_blocker[:100]}")

    # Jika tidak ada failing case tapi output kosong atau nggak ada section utama
    if not report.apa_yang_dilakukan and not report.failing_case:
        status = "revise"
        blockers.append("Laporan tidak memiliki section 'Apa yang dilakukan' — format mungkin tidak sesuai")

    return {
        "status": status,
        "reason": "; ".join(blockers) if blockers else "Output sesuai ekspektasi",
        "blockers": blockers,
    }


# ============================================================================
# Decide Phase
# ============================================================================

def decide_next_action(review_result: dict, current_subtask_idx: int,
                       total_subtasks: int, correction_count: int) -> dict:
    """
    Decide Phase: putuskan langkah berikutnya berdasarkan review.

    Args:
        review_result: dict dari review_agent2_report()
        current_subtask_idx: Index sub-tugas saat ini
        total_subtasks: Total sub-tugas
        correction_count: Berapa kali sudah dikoreksi untuk subtask ini

    Returns:
        dict dengan 'action' ('continue', 'revise', 'complete', 'escalate'),
        'reason', dan 'next_subtask_idx' (jika continue)
    """
    status = review_result["status"]

    # Kasus escalation
    if status in ("timeout", "crash", "stuck"):
        return {
            "action": "escalate",
            "reason": f"Sub-tugas gagal dengan status: {status}. Perlu intervensi user.",
            "next_subtask_idx": current_subtask_idx,
        }

    # Kasus revise (output salah)
    if status == "revise":
        if correction_count >= MAX_CORRECTIONS:
            return {
                "action": "escalate",
                "reason": f"Max {MAX_CORRECTIONS} koreksi sudah tercapai. Perlu intervensi user.",
                "next_subtask_idx": current_subtask_idx,
            }
        else:
            return {
                "action": "revise",
                "reason": f"Output perlu dikoreksi. Koreksi ke-{correction_count + 1}/{MAX_CORRECTIONS}.",
                "next_subtask_idx": current_subtask_idx,
                "correction_count": correction_count + 1,
            }

    # Kasus accept (lanjut ke subtask berikutnya)
    if status == "accept":
        if current_subtask_idx + 1 < total_subtasks:
            return {
                "action": "continue",
                "reason": f"Sub-tugas {current_subtask_idx + 1}/{total_subtasks} selesai. Lanjut ke berikutnya.",
                "next_subtask_idx": current_subtask_idx + 1,
                "correction_count": 0,  # Reset counter untuk subtask baru
            }
        else:
            return {
                "action": "complete",
                "reason": f"Semua {total_subtasks} sub-tugas selesai.",
                "next_subtask_idx": current_subtask_idx,
            }

    # Default: lanjut (untuk situasi tak terduga)
    return {
        "action": "continue",
        "reason": "Lanjut ke sub-tugas berikutnya",
        "next_subtask_idx": current_subtask_idx + 1,
        "correction_count": 0,
    }


# ============================================================================
# Main Orchestrator Loop
# ============================================================================

def run_orchestrator(task_description: str, plan_result: dict = None,
                     verbose: bool = False) -> dict:
    """
    Jalankan loop orchestrator lengkap: plan→delegate→review→decide→repeat.

    Args:
        task_description: Deskripsi task dari user
        plan_result: Optional pre-computed plan (dict dengan checklist + sub_tasks)
        verbose: Tampilkan detail setiap langkah

    Returns:
        dict dengan hasil orchestrator: summary, sub_tasks_selesai, laporan_final
    """
    # Step 1: Plan Phase
    if plan_result is None:
        plan_result = plan_task(task_description)

    checklist = plan_result["checklist"]
    sub_tasks = plan_result["sub_tasks"]
    total_subtasks = plan_result["total_subtasks"]

    if verbose:
        print("=" * 60)
        print("ORCA.PY — ORCHESTRATOR")
        print("=" * 60)
        print(f"Task: {task_description}")
        print(f"Sub-tugas: {total_subtasks}")
        print(f"Checklist: {len(checklist)} item")
        print()

    # Inisialisasi
    client = HermesClient(timeout_seconds=TASK_TIMEOUT_SECONDS, verbose=verbose)
    cycle_num = 1
    completed_subtasks = []
    failed_subtasks = []
    current_idx = 0
    correction_count = 0
    timeline = []

    # Loop utama
    while current_idx < total_subtasks:
        sub_task = sub_tasks[current_idx]
        subtask_id = sub_task["id"]

        if verbose:
            print(f"--- Sub-tugas {current_idx + 1}/{total_subtasks}: {subtask_id} ---")
            print(f"Deskripsi: {sub_task['description'][:100]}...")
            print()

        # Step 2: Delegate Phase
        if verbose:
            print("  [DELEGATE] Mengirim ke Hermes Agent...")

        delegasi_start = time.time()
        query_result = delegate_to_agent2(
            client=client,
            sub_task=sub_task,
            task_id=f"{subtask_id}-cycle{cycle_num}",
        )
        delegasi_duration = time.time() - delegasi_start

        # Step 3: Parse & Review Phase
        if verbose:
            print(f"  [DELEGATE] Response diterima ({query_result.duration_seconds:.1f}s)")

        agent2_report = parse_agent2_report(query_result.output)
        review_result = review_agent2_report(agent2_report, checklist)

        # Step 4: Decide Phase
        decide_result = decide_next_action(
            review_result=review_result,
            current_subtask_idx=current_idx,
            total_subtasks=total_subtasks,
            correction_count=correction_count,
        )

        # Log siklus
        log_cycle(
            cycle_num=cycle_num,
            trigger=task_description,
            plan_text=f"Sub-tugas: {sub_task['description'][:100]}",
            delegasi_text=f"Task ID: {subtask_id}, Duration: {query_result.duration_seconds:.1f}s",
            laporan_text=query_result.output[:500] if query_result.output else "(kosong)",
            review_text=review_result["reason"],
            keputusan=decide_result["action"],
        )

        # Track progress
        timeline.append({
            "subtask_id": subtask_id,
            "action": decide_result["action"],
            "review_status": review_result["status"],
            "duration": delegasi_duration,
        })

        if verbose:
            print(f"  [REVIEW] Status: {review_result['status']}")
            print(f"  [DECIDE] Action: {decide_result['action']}")
            print()

        # Eksekusi keputusan
        if decide_result["action"] == "continue":
            completed_subtasks.append(subtask_id)
            current_idx = decide_result["next_subtask_idx"]
            correction_count = decide_result.get("correction_count", 0)
            cycle_num += 1

            if verbose:
                print(f"  ✅ Lanjut ke sub-tugas berikutnya ({current_idx + 1}/{total_subtasks})")
                print()

        elif decide_result["action"] == "revise":
            correction_count = decide_result.get("correction_count", correction_count)

            if verbose:
                print(f"  🔄 Koreksi ke-{correction_count}/{MAX_CORRECTIONS}")
                print()

            # Tambahkan ke timeline sebagai revisi
            # (diimplementasikan sebagai retry pada sub-tugas yang sama)
            # Karena current_idx nggak berubah, loop akan mengulang sub-tugas ini
            # dengan prompt koreksi

            # Build koreksi prompt
            koreksi_prompt = f"""## Koreksi

Output sebelumnya tidak sesuai. Perbaiki berdasarkan:
- Task ID: {subtask_id}
- Deskripsi: {sub_task['description']}

Masalah yang dilaporkan: {review_result['reason']}

Silakan perbaiki dan lapor dalam format yang sama.
"""
            query_result = client.query(koreksi_prompt)
            agent2_report = parse_agent2_report(query_result.output)
            review_result = review_agent2_report(agent2_report, checklist)
            decide_result = decide_next_action(
                review_result=review_result,
                current_subtask_idx=current_idx,
                total_subtasks=total_subtasks,
                correction_count=correction_count - 1,  # sudah ditambahkan 1 di atas
            )

            # Log koreksi
            log_cycle(
                cycle_num=cycle_num,
                trigger=f"[KOREKSI] {task_description}",
                plan_text=f"Sub-tugas: {sub_task['description'][:100]}",
                delegasi_text=f"Koreksi ke-{correction_count}",
                laporan_text=query_result.output[:500] if query_result.output else "(kosong)",
                review_text=review_result["reason"],
                keputusan=decide_result["action"],
            )

            timeline.append({
                "subtask_id": subtask_id,
                "action": "revise",
                "review_status": review_result["status"],
                "duration": query_result.duration_seconds,
                "koreksi_ke": correction_count,
            })

            if decide_result["action"] == "continue":
                completed_subtasks.append(subtask_id)
                current_idx = decide_result["next_subtask_idx"]
                correction_count = decide_result.get("correction_count", 0)
                cycle_num += 1
            elif decide_result["action"] in ("escalate", "complete"):
                break

            if verbose:
                print(f"  [DECIDE] Action after koreksi: {decide_result['action']}")
                print()

        elif decide_result["action"] == "complete":
            completed_subtasks.append(sub_task["id"])
            if verbose:
                print(f"  🎯 Semua sub-tugas selesai!")
                print()
            break

        elif decide_result["action"] == "escalate":
            failed_subtasks.append(sub_task["id"])
            if verbose:
                print(f"  ⚠️ ESCALATION: {decide_result['reason']}")
                print()
            break

    # Step 5: Final Summary
    summary = {
        "task": task_description,
        "total_subtasks": total_subtasks,
        "completed_subtasks": len(completed_subtasks),
        "completed_ids": completed_subtasks,
        "failed_subtasks": len(failed_subtasks),
        "failed_ids": failed_subtasks,
        "timeline": timeline,
        "status": "completed" if current_idx >= total_subtasks else "partial",
    }

    if verbose:
        print("=" * 60)
        print("RINGKASAN SELESAI")
        print("=" * 60)
        print(f"Task: {task_description}")
        print(f"Sub-tugas selesai: {len(completed_subtasks)}/{total_subtasks}")
        print(f"Status: {summary['status']}")
        print()

    return summary


# ============================================================================
# V2: Multi-Agent Parallel Mode
# ============================================================================

def run_v2_parallel(task_description: str, plan_result: dict, verbose: bool = False, max_agents: int = 3) -> dict:
    """
    V2: Run orchestrator dengan multiple Agent 2 paralel (threading).

    - Dispatch sub-task ke multiple agents secara paralel
    - Non-blocking model (agents berjalan concurrent)
    - Shared task queue (multi-consumer)
    - Review tetap semi-otomatis (Agent 1 review, max 2x corrections)

    Args:
        task_description: Original task dari user
        plan_result: Hasil dari plan_task()
        verbose: Tampilkan detail
        max_agents: Max agent paralel (default: 3)

    Returns:
        Summary dict (sama format run_orchestrator)
    """
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed

    if verbose:
        print("=" * 60)
        print("ORCA.PY — RUN (V2: MULTI-AGENT PARALLEL)")
        print("=" * 60)
        print(f"Task: {task_description}")
        print(f"Sub-tugas: {plan_result['total_subtasks']}")
        print(f"Max agents: {max_agents}")
        print(f"Mode: parallel (threading)")
        print()

    sub_tasks = plan_result["sub_tasks"]
    total_subtasks = plan_result["total_subtasks"]
    cycle_num = 1

    completed_subtasks = []
    failed_subtasks = []
    timeline = []
    lock = threading.Lock()

    def execute_subtask(sub_task: dict, agent_id: str) -> dict:
        """Execute satu sub-task di thread terpisah."""
        subtask_id = sub_task["id"]
        subtask_desc = sub_task["description"]

        if verbose:
            print(f"  [AGENT-{agent_id}] Starting: {subtask_id}")

        # Set status agent running
        try:
            from status_tracker import StatusTracker
            tracker = StatusTracker()
            tracker.set_status(
                agent_id, "running",
                task_id=subtask_id,
                progress="0%",
            )
        except Exception:
            pass

        start_time = time.time()

        try:
            client = HermesClient(timeout_seconds=TASK_TIMEOUT_SECONDS, verbose=False)
            query_result = client.query_agent2(subtask_desc, task_id=subtask_id)

            duration = time.time() - start_time

            # Parse report
            report = parse_agent2_report(query_result.output)

            result = {
                "subtask_id": subtask_id,
                "agent_id": agent_id,
                "status": "completed" if report.apa_yang_dilakukan else "failed",
                "duration": duration,
                "timed_out": query_result.timed_out,
                "exit_code": query_result.exit_code,
                "failing_case": report.failing_case,
                "report": report,
                "output": query_result.output,
            }

            # Update status tracker
            try:
                from status_tracker import StatusTracker
                tracker = StatusTracker()
                tracker.set_status(
                    agent_id, "completed" if result["status"] == "completed" else "failed",
                    task_id=subtask_id,
                    failing_case=report.failing_case,
                    progress="100%",
                )
            except Exception:
                pass

        except Exception as e:
            duration = time.time() - start_time
            result = {
                "subtask_id": subtask_id,
                "agent_id": agent_id,
                "status": "failed",
                "duration": duration,
                "timed_out": False,
                "exit_code": -1,
                "failing_case": "CRASH",
                "error": str(e),
            }

        if verbose:
            status_icon = "✅" if result["status"] == "completed" else "❌"
            print(f"  {status_icon} [AGENT-{agent_id}] {subtask_id}: {result['status']} ({duration:.1f}s)")

        return result

    # Dispatch dengan ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_agents) as executor:
        future_to_task = {}

        for i, sub_task in enumerate(sub_tasks):
            agent_id = f"v2-agent-{i % max_agents + 1}"
            future = executor.submit(
                execute_subtask,
                sub_task,
                agent_id,
            )
            future_to_task[future] = sub_task

        # Collect results seiring completion (non-blocking V2)
        for future in as_completed(future_to_task):
            result = future.result()

            # Review hasil (semi-otomatis — Agent 1 review, max 2x)
            if result["failing_case"]:
                correction_count = 0
                review_result = {
                    "status": "reject",
                    "reason": f"Failing case: {result['failing_case']}",
                }

                while correction_count < MAX_CORRECTIONS and review_result["status"] == "reject":
                    correction_count += 1
                    if verbose:
                        print(f"  [KOREKSI-{correction_count}] {result['subtask_id']} via agent {result['agent_id']}")

                    koreksi_prompt = f"""## Task (Koreksi ke-{correction_count})

**ID**: {result['subtask_id']}
**Deskripsi**: {result['subtask_id']} — perbaiki berdasarkan masalah berikut:

Masalah yang dilaporkan: {review_result['reason']}

Silakan perbaiki dan lapor dalam format Agent 2 yang benar:
## Laporan Eksekusi Agent 2
- Task ID, Duration
- Apa yang dilakukan
- Hasil
- File yang diubah/dibuat
- Masalah/Blocker
- Saran berikutnya"""

                    try:
                        client = HermesClient(timeout_seconds=TASK_TIMEOUT_SECONDS, verbose=False)
                        query_result = client.query(koreksi_prompt)
                        report = parse_agent2_report(query_result.output)
                        review_result = review_agent2_report(report, plan_result["checklist"])

                        if review_result["status"] == "accept":
                            result["status"] = "completed"
                            result["failing_case"] = None
                            result["report"] = report

                            if verbose:
                                print(f"  ✅ [KOREKSI-{correction_count}] {result['subtask_id']} diterima")
                    except Exception as e:
                        pass

            with lock:
                timeline.append(result)

                if result["status"] == "completed":
                    completed_subtasks.append(result["subtask_id"])
                else:
                    failed_subtasks.append(result["subtask_id"])

                # Log cycle
                log_cycle(
                    cycle_num=cycle_num,
                    trigger=f"[V2] {task_description} — {result['subtask_id']} ({result['agent_id']})",
                    plan_text=result.get("report", {}).get("apapun", "")[:100] if result.get("report") else "",
                    delegasi_text=f"Agent V2: {result['agent_id']}",
                    laporan_text=result.get("output", "")[:500],
                    review_text=result.get("failing_case", "N/A"),
                    keputusan="completed" if result["status"] == "completed" else "escalate",
                )
                cycle_num += 1

    # Final summary
    summary = {
        "task": task_description,
        "total_subtasks": total_subtasks,
        "completed_subtasks": len(completed_subtasks),
        "completed_ids": completed_subtasks,
        "failed_subtasks": len(failed_subtasks),
        "failed_ids": failed_subtasks,
        "timeline": timeline,
        "status": "completed" if len(completed_subtasks) == total_subtasks else "partial",
        "mode": "v2_parallel",
        "agents_used": list(set(r["agent_id"] for r in timeline)),
    }

    if verbose:
        print()
        print("=" * 60)
        print("RINGKASAN V2 — MULTI-AGENT PARALLEL")
        print("=" * 60)
        print(f"Task: {task_description}")
        print(f"Sub-tugas selesai: {len(completed_subtasks)}/{total_subtasks}")
        print(f"Status: {summary['status']}")
        print(f"Agents used: {summary['agents_used']}")
        print()

    return summary


# ============================================================================
# CLI
# ============================================================================

def main():
    """CLI interface untuk orca.py."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Agent Calling Agent Builder — Orchestrator CLI",
        prog="orca.py",
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommand")

    # orca.py run <task>
    p_run = subparsers.add_parser("run", help="Jalankan orchestrator full cycle")
    p_run.add_argument("task", help="Deskripsi task yang akan dijalankan")
    p_run.add_argument("--verbose", "-v", action="store_true", help="Tampilkan detail setiap langkah")
    p_run.add_argument("--no-auto", action="store_true", help="Jangan auto-execute, hanya plan + tanya approval")
    p_run.add_argument("--mode", "-m", choices=["v1", "v2"], default="v1",
                       help="Execution mode: v1=sequential (hermes chat -q), v2=parallel (threading)")
    p_run.add_argument("--max-agents", type=int, default=3, help="Max agent paralel (V2 mode, default: 3)")

    # orca.py plan <task>
    p_plan = subparsers.add_parser("plan", help="Plan task menjadi sub-tugas + checklist")
    p_plan.add_argument("task", help="Deskripsi task")

    # orca.py status
    p_status = subparsers.add_parser("status", help="Lihat status agent/Agent 2")

    # orca.py logs
    p_logs = subparsers.add_parser("logs", help="Lihat log cycle terakhir")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        print("\nContoh penggunaan:")
        print("  python orca.py run \"Buat script Python fibonacci ke-N\"")
        print("  python orca.py run \"Buat script Python fibonacci ke-N\" --verbose")
        print("  python orca.py plan \"Buat script Python fibonacci ke-N\"")
        print("  python orca.py status")
        print("  python orca.py logs")
        sys.exit(0)

    # Command: plan
    if args.command == "plan":
        plan_result = plan_task(args.task)
        print("=" * 60)
        print("ORCA.PY — PLAN")
        print("=" * 60)
        print(f"Task: {args.task}")
        print(f"Sub-tugas: {plan_result['total_subtasks']}")
        print()
        print("### Checklist Tujuan")
        for i, item in enumerate(plan_result["checklist"], 1):
            print(f"- [ ] {item}")
        print()
        print("### Sub-tugas")
        for st in plan_result["sub_tasks"]:
            print(f"  - {st['id']}: {st['description']}")
            print(f"    Estimasi: {st['estimated_minutes']} menit")
        print()

        # Simpan plan ke JSON untuk referensi
        ensure_logs_dir()
        plan_file = LOGS_DIR / "status" / "last_plan.json"
        save_json(plan_file, {
            "task": args.task,
            "plan": plan_result,
            "timestamp": _now_iso(),
        })
        print(f"Plan tersimpan di: {plan_file}")

    # Command: run
    elif args.command == "run":
        if args.no_auto:
            # Plan saja, tanya approval
            plan_result = plan_task(args.task)
            print("=" * 60)
            print("ORCA.PY — PLAN (menunggu approval)")
            print("=" * 60)
            print(f"Task: {args.task}")
            print()
            print("### Checklist Tujuan")
            for i, item in enumerate(plan_result["checklist"], 1):
                print(f"- [ ] {item}")
            print()
            print("### Sub-tugas")
            for st in plan_result["sub_tasks"]:
                print(f"  - {st['id']}: {st['description']}")
            print()
            print("Jawab 'y' untuk lanjut eksekusi, 'n' untuk membatalkan:")
            response = input("> ").strip().lower()
            if response != 'y':
                print("Dibatalkan oleh user.")
                sys.exit(0)

        # Jalankan orchestrator
        plan_result = plan_task(args.task)
        if args.mode == "v2":
            summary = run_v2_parallel(
                task_description=args.task,
                plan_result=plan_result,
                verbose=args.verbose,
                max_agents=args.max_agents,
            )
        else:
            summary = run_orchestrator(
                task_description=args.task,
                plan_result=plan_result,
                verbose=args.verbose,
            )

        # Tampilkan ringkasan dalam format yang didokumentasikan di SKILL.md
        print()
        print("## Ringkasan Selesai")
        print()
        print(f"- Tujuan: {summary['task']}")
        print(f"- Sub-tugas selesai: {summary['completed_subtasks']}/{summary['total_subtasks']}")
        print(f"- Status: {summary['status']}")
        if summary['failed_subtasks'] > 0:
            print(f"- Gagal: {summary['failed_subtasks']} sub-tugas")
        print()

        # Status exit code
        if summary['status'] == 'completed':
            sys.exit(0)
        else:
            sys.exit(1)

    # Command: status
    elif args.command == "status":
        # Load status file jika ada
        status_data = load_json(STATUS_FILE)
        if status_data:
            print("=" * 60)
            print("ORCA.PY — STATUS AGENT")
            print("=" * 60)
            agents = status_data.get("agents", {})
            if agents:
                # Handle both dict format (status_tracker) dan list format
                if isinstance(agents, dict):
                    for agent_id, agent in agents.items():
                        if isinstance(agent, dict):
                            print(f"  Agent: {agent.get('id', agent_id)}")
                            print(f"    Status: {agent.get('status', 'N/A')}")
                            print(f"    Task: {agent.get('task_id', 'N/A')}")
                            print(f"    Progress: {agent.get('progress', 'N/A')}")
                            print()
                else:
                    for agent in agents:
                        print(f"  Agent: {agent.get('id', 'N/A')}")
                        print(f"    Status: {agent.get('status', 'N/A')}")
                        print(f"    Task: {agent.get('task_id', 'N/A')}")
                        print(f"    Progress: {agent.get('progress', 'N/A')}")
                        print()
            else:
                print("  Tidak ada agent yang terekam.")
        else:
            print("Belum ada status data.")
            print("Jalankan 'python orca.py run <task>' untuk memulai.")

    # Command: logs
    elif args.command == "logs":
        # Cari file log terbaru
        log_files = sorted(LOGS_DIR.glob("*_cycle_*.log"), reverse=True)
        if log_files:
            latest = log_files[0]
            print(f"Log terbaru: {latest.name}")
            print("=" * 60)
            with open(latest, "r", encoding="utf-8") as f:
                print(f.read())
        else:
            print("Belum ada log cycle.")


if __name__ == "__main__":
    main()

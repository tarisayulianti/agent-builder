#!/usr/bin/env python3
"""
status_tracker.py — Status Tracker untuk Agent Calling Agent Builder (V1)

Track status Agent 2: idle, running, completed, failed
Simpan di logs/status/agent_status.json
Handle 4 failing cases: TIMEOUT, CRASH, OUTPUT_MISMATCH, STUCK
"""
import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# Default paths
DEFAULT_STATUS_FILE = Path(__file__).parent / "logs" / "status" / "agent_status.json"
DEFAULT_QUEUE_FILE = Path(__file__).parent / "logs" / "queue" / "task_queue.json"
DEFAULT_HISTORY_FILE = Path(__file__).parent / "logs" / "history" / "task_history.json"


class StatusTracker:
    """Track status Agent 2 dan task history."""

    VALID_STATUSES = {"idle", "running", "completed", "failed", "timeout", "crash", "stuck"}

    def __init__(self, status_file: Optional[Path] = None, queue_file: Optional[Path] = None, history_file: Optional[Path] = None):
        self.status_file = status_file or DEFAULT_STATUS_FILE
        self.queue_file = queue_file or DEFAULT_QUEUE_FILE
        self.history_file = history_file or DEFAULT_HISTORY_FILE
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Pastikan folder logs ada."""
        for f in [self.status_file, self.queue_file, self.history_file]:
            f.parent.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path, default: dict) -> dict:
        """Load JSON file, return default jika tidak ada."""
        if path.exists():
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return default

    def _save_json(self, path: Path, data: dict) -> None:
        """Save data ke JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    # ── Agent Status ──────────────────────────────────────────────

    def get_status(self, agent_id: str = "agent2") -> dict:
        """Dapatkan status Agent 2."""
        data = self._load_json(self.status_file, {"agents": {}})
        return data.get("agents", {}).get(agent_id, self._default_agent_status(agent_id))

    def set_status(self, agent_id: str, status: str = "idle", **kwargs) -> dict:
        """Set status Agent 2. Valid status: idle, running, completed, failed, timeout, crash, stuck."""
        status = status.lower()
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}. Valid: {self.VALID_STATUSES}")

        data = self._load_json(self.status_file, {"agents": {}})

        if "agents" not in data:
            data["agents"] = {}
        if agent_id not in data["agents"]:
            data["agents"][agent_id] = self._default_agent_status(agent_id)

        agent = data["agents"][agent_id]
        agent["status"] = status
        agent["updated_at"] = datetime.now().isoformat()
        agent["updated_at_timestamp"] = time.time()

        for key, value in kwargs.items():
            if key == "task_id":
                agent["task_id"] = value
            elif key == "error":
                agent["error"] = value
            elif key == "failing_case":
                agent["failing_case"] = value
            elif key == "progress":
                agent["progress"] = value
            elif key == "notes":
                agent["notes"] = value

        self._save_json(self.status_file, data)
        return agent

    def update_progress(self, agent_id: str, task: str, progress: str) -> dict:
        """Update progress sub-tugas."""
        data = self._load_json(self.status_file, {"agents": {}})
        if "agents" not in data:
            data["agents"] = {}
        if agent_id not in data["agents"]:
            data["agents"][agent_id] = self._default_agent_status(agent_id)

        agent = data["agents"][agent_id]
        if "progress_log" not in agent:
            agent["progress_log"] = []

        entry = {
            "task": task,
            "progress": progress,
            "timestamp": datetime.now().isoformat(),
            "timestamp_timestamp": time.time(),
        }
        agent["progress_log"].append(entry)
        agent["updated_at"] = datetime.now().isoformat()
        agent["updated_at_timestamp"] = time.time()

        self._save_json(self.status_file, data)
        return agent

    def _default_agent_status(self, agent_id: str) -> dict:
        return {
            "id": agent_id,
            "status": "idle",
            "task_id": None,
            "error": None,
            "failing_case": None,
            "progress": "0%",
            "progress_log": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    # ── Task Queue ────────────────────────────────────────────────

    def enqueue_task(self, task_id: str, description: str, status: str = "pending") -> dict:
        """Tambah task ke queue."""
        data = self._load_json(self.queue_file, {"tasks": []})
        if "tasks" not in data:
            data["tasks"] = []

        task = {
            "task_id": task_id,
            "description": description,
            "status": status,
            "created_at": datetime.now().isoformat(),
        }
        data["tasks"].append(task)
        self._save_json(self.queue_file, data)
        return task

    def update_task_status(self, task_id: str, status: str) -> dict:
        """Update status task di queue."""
        data = self._load_json(self.queue_file, {"tasks": []})
        for task in data.get("tasks", []):
            if task["task_id"] == task_id:
                task["status"] = status
                task["updated_at"] = datetime.now().isoformat()
                break
        self._save_json(self.queue_file, data)
        return data

    def get_queue(self) -> list:
        """Dapatkan semua task di queue."""
        data = self._load_json(self.queue_file, {"tasks": []})
        return data.get("tasks", [])

    # ── Task History ──────────────────────────────────────────────

    def log_cycle(self, cycle_id: str, trigger: str, plan: str, delegate: str,
                  report: str, review: str, decision: str, agent_id: str = "agent2") -> dict:
        """Log satu siklus orchestrator."""
        data = self._load_json(self.history_file, {"cycles": []})
        if "cycles" not in data:
            data["cycles"] = []

        entry = {
            "cycle_id": cycle_id,
            "agent_id": agent_id,
            "trigger": trigger,
            "plan": plan,
            "delegate": delegate,
            "report": report,
            "review": review,
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
            "timestamp_timestamp": time.time(),
        }
        data["cycles"].append(entry)
        self._save_json(self.history_file, data)
        return entry

    def get_history(self, limit: int = 50) -> list:
        """Dapatkan riwayat siklus (terbaru pertama)."""
        data = self._load_json(self.history_file, {"cycles": []})
        cycles = data.get("cycles", [])
        return list(reversed(cycles))[:limit]

    # ── Failing Cases ─────────────────────────────────────────────

    def record_failing_case(self, agent_id: str, case_type: str,
                            task_id: str = None, error: str = None,
                            progress: str = None, notes: str = None) -> dict:
        """Record failing case dan set status agent."""
        case_map = {
            "TIMEOUT": "timeout",
            "CRASH": "crash",
            "OUTPUT_MISMATCH": "failed",
            "STUCK": "stuck",
        }
        status = case_map.get(case_type, "failed")
        return self.set_status(
            agent_id=agent_id,
            status=status,
            task_id=task_id,
            error=error,
            failing_case=case_type,
            progress=progress,
            notes=notes,
        )

    def clear_agent(self, agent_id: str) -> dict:
        """Reset status agent ke idle."""
        return self.set_status(agent_id, "idle")

    # ── V2: Multi-Agent Support ─────────────────────────────────────

    def register_agent(self, agent_id: str, **kwargs) -> dict:
        """Register agent baru ke status tracker."""
        status = kwargs.pop("status", "idle")
        return self.set_status(
            agent_id,
            status,
            **kwargs,
        )

    def get_all_agents(self) -> dict:
        """Dapatkan status SEMUA agent yang terdaftar."""
        data = self._load_json(self.status_file, {"agents": {}})
        return data.get("agents", {})

    def get_agent_count(self) -> int:
        """Hitung jumlah agent yang terdaftar."""
        return len(self.get_all_agents())

    def assign_task_to_agent(self, task_id: str, agent_id: str) -> dict:
        """Assign task ke agent tertentu di queue."""
        data = self._load_json(self.queue_file, {"tasks": []})
        for task in data.get("tasks", []):
            if task["task_id"] == task_id:
                task["agent_id"] = agent_id
                task["status"] = "assigned"
                task["assigned_at"] = datetime.now().isoformat()
                break
        self._save_json(self.queue_file, data)
        return data

    def get_queue_by_agent(self, agent_id: str) -> list:
        """Dapatkan task queue untuk agent tertentu."""
        data = self._load_json(self.queue_file, {"tasks": []})
        return [t for t in data.get("tasks", []) if t.get("agent_id") == agent_id]

    def get_running_agents(self) -> list:
        """Dapatkan daftar agent yang sedang running."""
        agents = self.get_all_agents()
        return [aid for aid, info in agents.items() if info.get("status") == "running"]

    def get_idle_agents(self) -> list:
        """Dapatkan daftar agent yang idle."""
        agents = self.get_all_agents()
        return [aid for aid, info in agents.items() if info.get("status") == "idle"]

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister agent (hapus dari status)."""
        data = self._load_json(self.status_file, {"agents": {}})
        if agent_id in data.get("agents", {}):
            del data["agents"][agent_id]
            self._save_json(self.status_file, data)
            return True
        return False

    # ── CLI ───────────────────────────────────────────────────────

    def _reset_test_state(self):
        """Reset state untuk test."""
        # Kosongkan agent status
        self._save_json(self.status_file, {"agents": {}})
        # Kosongkan task queue
        self._save_json(self.queue_file, {"tasks": []})
        # Kosongkan task history
        self._save_json(self.history_file, {"cycles": []})

    def test(self):
        """Test fungsi status_tracker."""
        print("=== status_tracker.py Test ===\n")

        # Reset state sebelum test
        self._reset_test_state()

        # Test set/get status
        print("[1] Test set_status / get_status")
        self.set_status("agent2", "running", task_id="test-001")
        status = self.get_status("agent2")
        print(f"  Status agent2: {status['status']}")
        print(f"  Task ID: {status['task_id']}")
        assert status["status"] == "running", "Status harus running"
        print("  ✅ PASS\n")

        # Test update_progress
        print("[2] Test update_progress")
        self.update_progress("agent2", "Sub-task 1", "Selesai 30%")
        status = self.get_status("agent2")
        print(f"  Progress log entries: {len(status['progress_log'])}")
        assert len(status["progress_log"]) >= 1
        print("  ✅ PASS\n")

        # Test failing case
        print("[3] Test record_failing_case")
        result = self.record_failing_case("agent2", "TIMEOUT", task_id="test-001",
                                          error="Timeout setelah 900 detik",
                                          progress="50%", notes="Akan di-spawn ulang")
        print(f"  Status setelah TIMEOUT: {result['status']}")
        print(f"  Failing case: {result['failing_case']}")
        assert result["status"] == "timeout"
        assert result["failing_case"] == "TIMEOUT"
        print("  ✅ PASS\n")

        # Test task queue
        print("[4] Test enqueue_task / get_queue")
        self.enqueue_task("task-001", "Buat script Python fibonacci")
        self.enqueue_task("task-002", "Review kode")
        queue = self.get_queue()
        print(f"  Jumlah task di queue: {len(queue)}")
        assert len(queue) == 2
        print("  ✅ PASS\n")

        # Test task history / log_cycle
        print("[5] Test log_cycle / get_history")
        self.log_cycle(
            cycle_id="cycle-001",
            trigger="Buat script Python fibonacci",
            plan="1. Buat fungsi fibonacci\n2. Test",
            delegate="Buat fungsi fibonacci",
            report="Fungsi fibonacci dibuat",
            review="✅ Accept",
            decision="lanjut",
        )
        history = self.get_history(limit=5)
        print(f"  Jumlah cycle di history: {len(history)}")
        assert len(history) >= 1
        print(f"  Cycle terbaru: {history[0]['cycle_id']}")
        print("  ✅ PASS\n")

        # Test clear_agent
        print("[6] Test clear_agent")
        self.clear_agent("agent2")
        status = self.get_status("agent2")
        print(f"  Status setelah clear: {status['status']}")
        assert status["status"] == "idle"
        print("  ✅ PASS\n")

        # Test V2: Multi-agent support
        print("[7] Test register_agent / get_all_agents (V2 multi-agent)")
        self._reset_test_state()
        self.register_agent("agent2", max_tasks=5)
        self.register_agent("agent3", max_tasks=3)
        all_agents = self.get_all_agents()
        print(f"  Jumlah agent terdaftar: {len(all_agents)}")
        assert len(all_agents) == 2, f"Expected 2 agents, got {len(all_agents)}"
        assert "agent3" in all_agents
        print("  ✅ PASS\n")

        # Test V2: get_queue_by_agent
        print("[8] Test assign_task_to_agent / get_queue_by_agent (V2)")
        self.enqueue_task("task-001", "Task untuk agent2")
        self.assign_task_to_agent("task-001", "agent2")
        queue_agent2 = self.get_queue_by_agent("agent2")
        print(f"  Task assigned to agent2: {len(queue_agent2)}")
        assert len(queue_agent2) == 1
        assert queue_agent2[0]["agent_id"] == "agent2"
        print("  ✅ PASS\n")

        # Test V2: get_running_agents / get_idle_agents
        print("[9] Test get_running_agents / get_idle_agents (V2)")
        self.set_status("agent2", "running")
        self.set_status("agent3", "idle")
        running = self.get_running_agents()
        idle = self.get_idle_agents()
        print(f"  Running: {running}")
        print(f"  Idle: {idle}")
        assert "agent2" in running
        assert "agent3" in idle
        print("  ✅ PASS\n")

        # Test V2: unregister_agent
        print("[10] Test unregister_agent (V2)")
        self.unregister_agent("agent3")
        all_agents = self.get_all_agents()
        print(f"  Agent setelah unregister: {len(all_agents)}")
        assert "agent3" not in all_agents
        print("  ✅ PASS\n")

        # Cleanup
        self._reset_test_state()
        self.register_agent("agent2")

        print("=== Semua test PASS (10/10) ===")
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agent Calling Agent Builder — Status Tracker")
    parser.add_argument("--test", action="store_true", help="Run test suite")
    parser.add_argument("--status", action="store_true", help="Show current agent status")
    parser.add_argument("--agent", default="agent2", help="Agent ID (default: agent2)")
    parser.add_argument("--agents", action="store_true", help="Show ALL agents status (V2)")
    parser.add_argument("--reset", action="store_true", help="Reset status, queue, history")

    args = parser.parse_args()
    tracker = StatusTracker()

    if args.reset:
        tracker._reset_test_state()
        tracker.register_agent("agent2")
        print("✅ Status reset & agent2 registered")
        exit(0)

    if args.agents:
        all_agents = tracker.get_all_agents()
        print(f"=== Semua Agent ({len(all_agents)} terdaftar) ===")
        print()
        for aid, info in all_agents.items():
            print(f"Agent: {aid}")
            print(f"  Status: {info.get('status', 'unknown')}")
            print(f"  Task ID: {info.get('task_id', 'None')}")
            print(f"  Progress: {info.get('progress', '0%')}")
            print(f"  Failing case: {info.get('failing_case', 'None')}")
            print(f"  Updated: {info.get('updated_at', 'N/A')}")
            print()
        running = tracker.get_running_agents()
        idle = tracker.get_idle_agents()
        print(f"Running: {running}")
        print(f"Idle: {idle}")
        exit(0)

    if args.test:
        success = tracker.test()
        exit(0 if success else 1)

    if args.status:
        status = tracker.get_status(args.agent)
        print(f"Agent: {status['id']}")
        print(f"Status: {status['status']}")
        print(f"Task ID: {status['task_id'] or 'None'}")
        print(f"Progress: {status['progress']}")
        print(f"Failing case: {status['failing_case'] or 'None'}")
        print(f"Updated: {status['updated_at']}")
        if status.get('error'):
            print(f"Error: {status['error']}")
        exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()

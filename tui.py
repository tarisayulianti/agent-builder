#!/usr/bin/env python
"""
TUI (Terminal User Interface) untuk Agent Builder.

Interface interaktif yang memudahkan penggunaan orca.py
tanpa perlu mengingat perintah CLI panjang.

Usage:
    python tui.py
"""
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

PYTHON = sys.executable


class TUIApp:
    """Simple TUI untuk Agent Builder."""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.status_file = self.project_root / "logs" / "status" / "agent_status.json"
        self.history_file = self.project_root / "logs" / "history" / "task_history.json"

    def _safe_input(self, prompt=""):
        """Wrapper untuk input() — handle EOFError pada piped input."""
        try:
            return input(prompt)
        except EOFError:
            return ""

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        self.clear()
        print("=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def print_menu(self):
        print("\n📋 MAIN MENU:\n")
        print("  [1] Jalankan task baru")
        print("  [2] Lihat status agent")
        print("  [3] Lihat task history")
        print("  [4] Reset semua status")
        print("  [5] Buka dashboard")
        print("  [6] Test (self-test)")
        print("  [7] Keluar")
        print("\n" + "-" * 60)

    def get_status_summary(self):
        """Baca status singkat dari file JSON."""
        try:
            with open(self.status_file, 'r') as f:
                data = json.load(f)
            agents = data.get('agents', {})
            running = [a for a, info in agents.items() if info.get('status') == 'running']
            idle = [a for a, info in agents.items() if info.get('status') == 'idle']
            return f"Agent: {len(agents)} total | RUN: {len(running)} | IDLE: {len(idle)}"
        except FileNotFoundError:
            return "Agent: 0 (belum berjalan)"
        except Exception:
            return "Agent: status unavailable"

    def get_history_summary(self):
        """Baca ringkasan history."""
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            cycles = data.get('cycles', [])
            completed = [c for c in cycles if c.get('keputusan') == 'complete']
            return f"Cycles: {len(cycles)} total | {len(completed)} completed"
        except FileNotFoundError:
            return "History: none"
        except Exception:
            return "History: unavailable"

    def run_task(self):
        """Input task dan execute via orca.py."""
        self.print_header("RUN NEW TASK")
        print("\nDescribe task (e.g. 'buat script python fibonacci ke-10')")
        print("Leave empty to cancel.\n")
        task = self._safe_input("> ").strip()
        if not task:
            print("\nCancelled.")
            self._safe_input("\nPress Enter to continue...")
            return

        print(f"\nRunning task: {task}")
        print("  This may take 2-20 minutes depending on complexity.\n")

        cmd = [PYTHON, str(self.project_root / "orca.py"), "run", task, "--verbose"]

        print(f"Command: {' '.join(cmd)}\n")
        print("-" * 60)

        try:
            result = subprocess.run(cmd, cwd=str(self.project_root))
            if result.returncode == 0:
                print("\nTask complete!")
            else:
                print(f"\nTask exited with code: {result.returncode}")
        except KeyboardInterrupt:
            print("\n\nInterrupted.")
        except Exception as e:
            print(f"\nError: {e}")

        self._safe_input("\nPress Enter to continue...")

    def view_status(self):
        """Tampilkan status agent."""
        self.print_header("AGENT STATUS")
        print(f"\n{self.get_status_summary()}")
        print(f"\n{self.get_history_summary()}\n")

        try:
            with open(self.status_file, 'r') as f:
                data = json.load(f)
            agents = data.get('agents', {})
            if agents:
                print("Details:")
                for name, info in agents.items():
                    status = info.get('status', 'unknown')
                    task = info.get('current_task', 'None')
                    icon = "[running]" if status == 'running' else "[idle]" if status == 'idle' else "[offline]"
                    print(f"  {icon} {name}: {status} (task: {task})")
        except Exception:
            pass

        self._safe_input("\nPress Enter to continue...")

    def view_history(self):
        """Tampilkan task history."""
        self.print_header("TASK HISTORY")
        try:
            with open(self.history_file, 'r') as f:
                data = json.load(f)
            cycles = data.get('cycles', [])
            if not cycles:
                print("\n  (no history)")
            else:
                print(f"\n  Total cycles: {len(cycles)}\n")
                for c in reversed(cycles[-15:]):
                    cycle_num = c.get('cycle', '?')
                    keputusan = c.get('keputusan', '?')
                    trigger = str(c.get('trigger', '?'))[:50]
                    icon = "[done]" if keputusan == 'complete' else "[loop]" if keputusan == 'continue' else "?"
                    print(f"  {icon} Cycle {cycle_num}: {keputusan} - {trigger}")
        except FileNotFoundError:
            print("\n  (history file not found)")
        except Exception as e:
            print(f"\n  Error: {e}")

        self._safe_input("\nPress Enter to continue...")

    def reset_status(self):
        """Reset semua status — via template copy, not orca.py reset."""
        self.print_header("RESET ALL STATUS")
        print("\n  This clears all agent status, queue, and history.")
        print("  Type 'YES' to confirm.")

        confirm = self._safe_input("\n> ").strip()
        if confirm != "YES":
            print("\nCancelled.")
            self._safe_input("\nPress Enter...")
            return

        print("\nResetting...")
        for name in ['agent_status.json', 'task_queue.json', 'task_history.json']:
            src = self.project_root / "logs" / name
            template = self.project_root / "logs" / "template" / name
            if template.exists():
                shutil.copy2(template, src)
                print(f"  Reset {name}")
        print("\nDone.")
        self._safe_input("\nPress Enter...")

    def open_dashboard(self):
        """Generate and open dashboard."""
        self.print_header("DASHBOARD")
        print("\n  Generating dashboard...")

        dashboard_script = self.project_root / "dashboard" / "dashboard.py"
        if dashboard_script.exists():
            result = subprocess.run(
                [PYTHON, str(dashboard_script), "--generate"],
                cwd=str(self.project_root),
                capture_output=True, text=True
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            html_path = self.project_root / "dashboard" / "index.html"
            print(f"  Dashboard: {html_path}")
            print("  Open in browser: dashboard/index.html")
        else:
            print("\n  dashboard.py not found")

        self._safe_input("\nPress Enter...")

    def run_tests(self):
        """Run self-test."""
        self.print_header("SELF-TEST")
        print("\n  Running tests...\n")
        print("-" * 60)

        cmd1 = [PYTHON, str(self.project_root / "status_tracker.py"), "--test"]
        cmd2 = [PYTHON, str(self.project_root / "hermes_client.py"), "--test"]

        for label, cmd in [("status_tracker", cmd1), ("hermes_client", cmd2)]:
            print(f"\n  [{label}]")
            result = subprocess.run(cmd, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            for line in lines[-3:]:
                print(f"    {line}")
            if result.returncode != 0:
                print(f"    EXIT: {result.returncode}")

        print("\n" + "-" * 60)
        print("\nTests complete.")
        self._safe_input("\nPress Enter...")

    def run(self):
        while True:
            self.clear()
            print("=" * 60)
            print("  AGENT BUILDER - TERMINAL UI")
            print("=" * 60)

            self.print_menu()
            print(self.get_status_summary())
            print(self.get_history_summary())
            print()

            try:
                choice = self._safe_input("\nPilih [1-7]: ").strip()
            except KeyboardInterrupt:
                print("\n\nBye!")
                break

            if not choice:
                continue

            if choice == "1":
                self.run_task()
            elif choice == "2":
                self.view_status()
            elif choice == "3":
                self.view_history()
            elif choice == "4":
                self.reset_status()
            elif choice == "5":
                self.open_dashboard()
            elif choice == "6":
                self.run_tests()
            elif choice == "7":
                print("\nBye!")
                break
            else:
                if choice:
                    print(f"\n  Invalid: '{choice}'")
                self._safe_input("\n  Press Enter...")


if __name__ == "__main__":
    app = TUIApp()
    app.run()

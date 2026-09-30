#!/usr/bin/env python
"""
Dashboard generator untuk Agent Builder.

Generate static HTML showing agent status, task history.
Optionally serve via HTTP.

Usage:
    python dashboard.py --generate     # Buat HTML file
    python dashboard.py --serve        # Serve via HTTP (port 8080)
    python dashboard.py --serve --open # Serve + buka di browser
"""
import os
import sys
import json
import argparse
import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.absolute()

STATUS_FILE = PROJECT_ROOT / "logs" / "status" / "agent_status.json"
HISTORY_FILE = PROJECT_ROOT / "logs" / "history" / "task_history.json"
QUEUE_FILE = PROJECT_ROOT / "logs" / "queue" / "task_queue.json"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agent Builder Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #1a1a27;
      color: #e0e0e0;
      padding: 20px;
    }
    .header {
      text-align: center;
      padding: 20px 0;
      border-bottom: 2px solid #16213e;
      margin-bottom: 20px;
    }
    .header h1 { color: #00d4ff; font-size: 1.8em; }
    .header .timestamp { color: #888; font-size: 0.9em; margin-top: 5px; }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-bottom: 30px;
    }
    .stat-card {
      background: #16213e;
      border-radius: 10px;
      padding: 20px;
      text-align: center;
      border: 1px solid #0f3460;
    }
    .stat-card .number { font-size: 2.5em; font-weight: bold; color: #00d4ff; }
    .stat-card .label { color: #888; font-size: 0.9em; margin-top: 5px; }
    .card {
      background: #16213e;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
      border: 1px solid #0f3460;
    }
    .card h2 { color: #00d4ff; margin-bottom: 15px; font-size: 1.2em; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #0f3460; }
    th { color: #00d4ff; }
    .status-badge {
      display: inline-block;
      padding: 3px 10px;
      border-radius: 15px;
      font-size: 0.8em;
      font-weight: bold;
    }
    .status-running { background: #0f3460; color: #00d4ff; }
    .status-idle { background: #0f3460; color: #888; }
    .status-complete { background: #0a5c2c; color: #00ff88; }
    .status-revise { background: #5c3a0a; color: #ffaa00; }
    .status-accept { background: #0a5c2c; color: #00ff88; }
    .no-data { color: #888; text-align: center; padding: 30px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Agent Builder Dashboard</h1>
    <div class="timestamp">Last updated: __TIMESTAMP__</div>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="number">__AGENT_COUNT__</div>
      <div class="label">Active Agents</div>
    </div>
    <div class="stat-card">
      <div class="number">__RUNNING__</div>
      <div class="label">Running</div>
    </div>
    <div class="stat-card">
      <div class="number">__TOTAL_CYCLES__</div>
      <div class="label">Total Cycles</div>
    </div>
    <div class="stat-card">
      <div class="number">__COMPLETED__</div>
      <div class="label">Tasks Completed</div>
    </div>
  </div>

  <div class="card">
    <h2>Agent Status</h2>
    __AGENT_TABLE__
  </div>

  <div class="card">
    <h2>Recent Task History</h2>
    __HISTORY_TABLE__
  </div>
</body>
</html>"""


def read_json(path):
    """Read JSON file safely."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def generate_html():
    """Generate dashboard HTML from log files."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Read status
    status_data = read_json(STATUS_FILE) or {
        "agents": {},
        "total_tasks_completed": 0
    }
    agents = status_data.get("agents", {})
    total_completed = status_data.get("total_tasks_completed", 0)

    running_count = sum(1 for a in agents.values() if a.get("status") == "running")

    # Build agent table
    if agents:
        agent_rows = ""
        for name, info in sorted(agents.items()):
            status = info.get("status", "unknown")
            task = info.get("current_task", "None")
            badge_class = f"status-{status}" if status != "completed" else "status-complete"
            agent_rows += f"<tr><td><span class='status-badge {badge_class}'>{status}</span></td><td>{name}</td><td>{task}</td></tr>"
        agent_table = f"""
        <table>
          <tr><th>Status</th><th>Agent Name</th><th>Current Task</th></tr>
          {agent_rows}
        </table>"""
    else:
        agent_table = "<div class='no-data'>No agents registered</div>"

    # Read history
    history_data = read_json(HISTORY_FILE)
    cycles = history_data.get("cycles", []) if history_data else []
    total_cycles = len(cycles)
    completed_cycles = sum(1 for c in cycles if c.get("keputusan") == "complete")

    if cycles:
        history_rows = ""
        for c in reversed(cycles[-10:]):
            cycle_num = c.get("cycle", "?")
            keputusan = c.get("keputusan", "?")
            trigger = str(c.get("trigger", ""))[:40]
            time = c.get("timestamp", "")[-8:] if c.get("timestamp") else ""
            badge_class = f"status-{keputusan}" if keputusan in ["accept", "continue", "complete", "revise"] else ""
            history_rows += f"<tr><td>Cycle {cycle_num}</td><td><span class='status-badge {badge_class}'>{keputusan}</span></td><td>{trigger}</td><td>{time}</td></tr>"
        history_table = f"""
        <table>
          <tr><th>Cycle</th><th>Status</th><th>Task</th><th>Time</th></tr>
          {history_rows}
        </table>"""
    else:
        history_table = "<div class='no-data'>No task history</div>"

    # Fill template
    html = HTML_TEMPLATE
    html = html.replace("__TIMESTAMP__", timestamp)
    html = html.replace("__AGENT_COUNT__", str(len(agents)))
    html = html.replace("__RUNNING__", str(running_count))
    html = html.replace("__TOTAL_CYCLES__", str(total_cycles))
    html = html.replace("__COMPLETED__", str(completed_cycles))
    html = html.replace("__AGENT_TABLE__", agent_table)
    html = html.replace("__HISTORY_TABLE__", history_table)

    # Write HTML
    output_path = PROJECT_ROOT / "dashboard" / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"[Dashboard] Generated: {output_path}")
    print(f"[Stats] Agents: {len(agents)}, Running: {running_count}, Cycles: {total_cycles}, Completed: {completed_cycles}")
    return str(output_path)


def serve(port=8080, open_browser=True):
    """Serve dashboard via HTTP."""
    import http.server
    import threading
    import webbrowser

    generate_html()

    handler = http.server.HTTPServer(
        ('', port), http.server.SimpleHTTPRequestHandler
    )
    os.chdir(PROJECT_ROOT / "dashboard")

    print(f"[Dashboard] Serving at http://localhost:{port}")
    if open_browser:
        threading.Thread(lambda: webbrowser.open(f"http://localhost:{port}"), daemon=True).start()

    try:
        handler.serve_forever()
    except KeyboardInterrupt:
        print("\n[Dashboard] Stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent Builder Dashboard")
    parser.add_argument("--generate", action="store_true", help="Generate HTML file only")
    parser.add_argument("--serve", action="store_true", help="Serve via HTTP")
    parser.add_argument("--port", type=int, default=8080, help="HTTP port (default: 8080)")
    parser.add_argument("--open", action="store_true", help="Open in browser")

    args = parser.parse_args()

    if args.serve:
        serve(port=args.port, open_browser=args.open)
    else:
        generate_html()

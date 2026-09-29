# V4 — External Project Management Integration

## Status: 🔲 V4 — Belum mulai (V3 belum dimulai)

## Visi
Integrasi dengan sistem project management eksternal (Jira, Trello) untuk sinkronisasi task antara agent-builder dan platform PM.

## Environment Setup
```bash
# 1. Install PM integration dependencies
pip install jira trello-python requests

# 2. Set environment variables (.env)
cp 05-configuration/.env.example .env
# Edit .env dengan credentials Jira/Trello

# 3. Test connection
python pm/jira_client.py --ping
python pm/trello_client.py --ping

# 4. Sync tasks
python pm/integration.py --sync-from-platform
python pm/integration.py --sync-to-platform
```

## Komponen V4
| Komponen | File | Status |
|---|---|---|
| Jira client | `pm/jira_client.py` | 🔲 |
| Trello client | `pm/trello_client.py` | 🔲 |
| PM integration module | `pm/integration.py` | 🔲 |

## Configuration (.env)
```env
# Jira
JIRA_API_TOKEN=<token>
JIRA_BASE_URL=https://<your-domain>.atlassian.net
JIRA_PROJECT_KEY=AGT

# Trello
TRELLO_API_KEY=<key>
TRELLO_TOKEN=<token>
TRELLO_BOARD_ID=<id>
TRELLO_LIST_MAPPING={"todo":"abc123","inprogress":"def456","done":"ghi789"}
```

## Supported Platforms
1. **Jira** — Sync task, create issues, update status
2. **Trello** — Sync cards, create/update, move between lists

## Jira Integration
```bash
# Create Jira issue dari task
python pm/jira_client.py --create-issue \
  --summary "Buat script fibonacci" \
  --description "Detailed task description" \
  --assignee "agent-2"

# Update issue status
python pm/jira_client.py --update-issue \
  --issue-key AGT-123 \
  --status "In Progress"
```

## Trello Integration
```bash
# Create Trello card dari task
python pm/trello_client.py --create-card \
  --name "Buat script fibonacci" \
  --desc "Detailed task description" \
  --list-id abc123

# Move card between lists
python pm/trello_client.py --move-card \
  --card-id xyz789 \
  --list-id def456
```

## Test Commands
```bash
# Test Jira connection
python pm/jira_client.py --ping

# Test Trello connection
python pm/trello_client.py --ping

# Sync all tasks (dry-run)
python pm/integration.py --sync-from-platform --dry-run

# Sync specific task
python pm/integration.py --sync-task task-001
```

## Dependencies
- `jira` library (Python Jira client)
- `trello-python` library (Python Trello client)
- `requests` library (HTTP client)

## File Structure
```
pm/
├── jira_client.py      # Jira API integration
├── trello_client.py    # Trello API integration
├── integration.py      # Orchestration layer (sync logic)
├── config.py           # Config loader
├── README.md           # Setup & usage guide
└── tests/
    ├── test_jira.py
    └── test_trello.py
```

## Migration Path (V3 → V4)
1. Install PM integration dependencies
2. Configure API tokens di .env
3. Test connectivity ke platform
4. Enable sync in orca.py (config: `PM_SYNC_ENABLED=true`)
5. Test bidirectional sync

## Integration Points
- `pm/integration.py` ↔ `orca.py` (task status sync)
- `pm/integration.py` ↔ `status_tracker.py` (status update)
- `pm/jira_client.py` ↔ `pm/trello_client.py` (shared interface)
- `pm/integration.py` ↔ `logs/history/task_history.json` (history sync)

## Next Action
Implementation setelah V3 selesai.
Lihat juga: [V3 Task Optimizer](V3_TASK_OPTIMIZER.md)

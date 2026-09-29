# V5 — Web Dashboard & Real-time Monitoring

## Status: 🔲 V5 — Belum mulai (V4 belum dimulai)

## Visi
Web dashboard real-time untuk monitoring agent status, task queue, log siklus, dan notifikasi adversarial review.

## Environment Setup
```bash
# 1. Install backend dependencies
pip install fastapi uvicorn websockets

# 2. Install frontend dependencies
cd web/static
npm install
npm run build

# 3. Start server
python websocket/server.py

# 4. Open browser
http://localhost:8080
```

## Komponen V5
| Komponen | File | Status |
|---|---|---|
| WebSocket server | `websocket/server.py` | 🔲 |
| Web static | `web/static/index.html` | 🔲 |
| CSS framework | `web/static/style.css` | 🔲 |
| JS client | `web/static/app.js` | 🔲 |
| Template | `websocket/templates/` | 🔲 |

## Configuration (.env)
```env
# V5 settings
WEB_DASHBOARD_ENABLED=true
WEB_HOST=localhost
WEB_PORT=8080
WS_HOST=0.0.0.0
WS_PORT=8081
AUTH_ENABLED=false
```

## Features
- Real-time status update via WebSocket
- Task queue visualization
- Cycle log viewer
- Adversarial review notification
- Dark/light mode toggle

## Test Commands
```bash
# Start dashboard server
python websocket/server.py &

# Check server health
curl http://localhost:8080/health

# Open dashboard
echo "Open: http://localhost:8080"

# Check WebSocket connection
python -c "import websockets; ws = websockets.connect('ws://localhost:8081'); print('WS OK')"

# Stop server
pkill -f websocket/server.py
```

## Dependencies
- **Backend**: Python (fastapi, uvicorn, websockets)
- **Frontend**: Node.js + npm (for building static assets)
- **Browser**: Chrome, Firefox, Edge (modern JS support)

## File Structure
```
websocket/
├── server.py          # WebSocket server
├── api.py              # REST API endpoints
├── templates/
│   ├── index.html
│   └── dashboard.html
└── tests/
    └── test_server.py

web/
├── static/
│   ├── index.html      # Main dashboard page
│   ├── style.css       # Styling
│   ├── app.js          # Frontend logic
│   └── components/     # Reusable UI components
└── README.md
```

## Migration Path (V4 → V5)
1. Install WebSocket + FastAPI dependencies
2. Set up static file serving
3. Create dashboard UI (index.html)
4. Implement WebSocket real-time updates
5. Enable in orca.py (`WEB_DASHBOARD_ENABLED=true`)

## Integration Points
- `websocket/server.py` ↔ `status_tracker.py` (status streaming)
- `websocket/server.py` ↔ `logs/` (real-time log feed)
- `web/static/app.js` ↔ `websocket/server.py` (WebSocket client)
- `websocket/server.py` ↔ `orca.py` (orchestrator events)

## Security Notes
- Default: `AUTH_ENABLED=false` (development)
- Production: set `AUTH_ENABLED=true` and configure authentication
- CORS: configure in FastAPI for production access

## Next Action
Implementation setelah V4 selesai.
Lihat juga: [V4 PM Integration](V4_PM_INTEGRATION.md)

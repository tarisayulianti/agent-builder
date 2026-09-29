# Panduan Integration Test — Agent Calling Agent Builder

**Status:** READY  
**Dibuat:** 2026-09-27  
**Lokasi:** `~/agent-builder-docs/06-testing/INTEGRATION_TEST_GUIDE.md`

---

## 📋 Tujuan

Panduan ini menjelaskan cara menjalankan integration test untuk memverifikasi bahwa sistem Agent Calling Agent Builder terstruktur dengan benar dan komponen-komponen penting berfungsi.

---

## 📁 Prasyarat

- Folder project ada di `F:/AI-AGENT/agent-builder/` (tempat file code & dokumen berada)
- Folder dokumentasi di `~/agent-builder-docs/`
- Python 3 tersedia di lingkungan
- Bash tersedia di lingkungan

---

## 🚀 Cara Menjalankan Test

```bash
cd ~/agent-builder
bash scripts/integration_test.sh
```

Test akan menjalankan serangkaian pemeriksaan otomatis dan melaporkan hasilnya.

---

## 📊 Apa yang Di-test

### 1. File Kunci (20+ file)
Memeriksa keberadaan file-file dokumentasi & utilitas penting:
- Dokumen: SKILL.md, AGENT2_INSTRUCTION.md, EXAMPLE_CHAT_TRIGGER.md, PLAN.md, BLUEPRINT.md, ARCHITECTURE_DIAGRAM.html, IMPLEMENTATION_PLAN.md, README.md, .env.example
- Skill: skills/orchestrator/SKILL.md, skills/orchestrator/context.md, skills/executor/SKILL.md, skills/executor/instruction_short.md
- Utilitas: status_tracker.py, spawn_agent2.sh, bin/agent-builder
- Storage: logs/status/agent_status.json, logs/queue/task_queue.json, logs/history/task_history.json

### 2. status_tracker.py
- Test add agent baru
- Test list semua agent
- Test update status agent
- Test get detail agent
- Test cleanup (kill agent)

### 3. spawn_agent2.sh
- Test syntax bash
- Test usage message
- Test handle argumen tidak lengkap

### 4. bin/agent-builder
- Test syntax bash
- Test usage message
- Test --help command
- Test status command
- Test invalid command handling

### 5. ML Task Optimizer
- Test stats command
- Test recommend command
- Test log task
- Test data tersimpan di stats

### 6. Advanced ML
- Test script berjalan
- Test stats output

### 7. API Server
- Test syntax Python
- Cek Flask availability

### 8. WebSocket Server
- Test syntax Python
- Cek websockets availability

### 9. PM & CI/CD Clients
- Test syntax 4 file: jira_client.py, trello_client.py, jenkins_client.py, gitlab_client.py

### 10. Docker & K8s Configs
- Test keberadaan file: Dockerfile.agent2, docker-compose.yml, deployment.yaml
- Test struktur valid: version, services, FROM, CMD, apiVersion, kind

### 11. Web Dashboard
- Test keberadaan file: index.html
- Test struktur: HTML doctype, WebSocket

### 12. Konfigurasi
- Test keberadaan .env.example
- Test variabel konfigurasi: HERMES_MODEL, TIMEOUT_MINUTES

---

## 📈 Interpretasi Hasil

Test melaporkan dalam format:
- ✅ PASS: <deskripsi> — test berhasil
- ❌ FAIL: <deskripsi> — test gagal
- ℹ️ INFO: <deskripsi> — informasi (bukan pass/fail)

**Ringkasan di akhir:**
```
Total test: N
✅ Passed: X
❌ Failed: Y
```

**Kriteria selesai:**
- Jika ❌ Failed = 0 → sistem siap untuk V2 development
- Jika ❌ Failed > 0 → perbaiki sebelum lanjut V2

---

## 🧪 Contoh Output

```
═
Agent Calling Agent Builder — Integration Test
═

── 1. File Kunci ──
✅ PASS: Ada: SKILL.md
✅ PASS: Ada: AGENT2_INSTRUCTION.md
...
✅ PASS: Ada: status_tracker.py

── 2. status_tracker.py ──
✅ PASS: add: berhasil
✅ PASS: list: melihat agent yang ditambah
✅ PASS: update: berhasil
✅ PASS: get: berhasil mendapatkan agent

── 5. ML Task Optimizer ──
✅ PASS: ml/task_optimizer.py: stats command berfungsi
✅ PASS: ml/task_optimizer.py: recommend command berfungsi
✅ PASS: ml/task_optimizer.py: log task berfungsi

═══════════════════════════════════════════════════
RINGKASAN
═══════════════════════════════════════════════════
Total test: 54
✅ Passed: 54
❌ Failed: 0

✅ Semua test passed. Sistem siap untuk V2 development.
```

---

## ⚠️ Catatan

- Test structural/format, bukan behavioral test (karena butuh Hermes CLI + tmux untuk test nyata)
- Beberapa komponen (API server, WebSocket server) butuh dependency tambahan (flask, websockets) untuk dijalankan
- V2 behavioral loop (tmux multi-agent) tidak bisa di-test di environment tanpa tmux
- Integration test cocok untuk verifikasi struktur project sebelum implementasi V2+

---

**Untuk menjalankan test:**
```bash
cd ~/agent-builder
bash scripts/integration_test.sh
```

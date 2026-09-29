# Contoh Chat Trigger & Respons

**Status:** READY  
**Lokasi:** `F:/AI-AGENT/agent-builder/EXAMPLE_CHAT_TRIGGER.md`

---

## Contoh 1: Membuat Script Sederhana

### Trigger User:
```
> Buat script Python untuk menghitung fibonacci ke-N
```

### Respons Agent 1 (Orchestrator):
```
## Perencanaan

Tujuan: Script Python fibonacci(N) yang bisa dijalankan dari command line.

### Checklist Tujuan
- [ ] Script `fibonacci.py` dibuat dengan fungsi fibonacci(N)
- [ ] Support CLI argument (python fibonacci.py 10)
- [ ] Handle edge case (N < 0, N = 0, N = 1)
- [ ] Basic test/verifikasi script berjalan

---

## Delegasi ke Agent 2

### Task 1: Buat script dasar
Silakan buat `fibonacci.py` dengan:
- Fungsi fibonacci(N) yang return N-th fibonacci number
- CLI interface: `python fibonacci.py <N>`
- Handle N < 0 dengan error message

Laporan dalam format Agent 2 standard.
```

### Laporan Agent 2 (langsung ke Agent 1 via delegate_task result):
```markdown
## Laporan Eksekusi Agent 2

**Task ID**: task-001
**Duration**: ~5 menit

### Apa yang dilakukan
Membuat script `fibonacci.py` sesuai spesifikasi.

### Hasil
- Script berjalan: `python fibonacci.py 10` → 55
- Handle N=0 → 0, N=1 → 1
- Error handling untuk N < 0

### File yang diubah/dibuat
- `fibonacci.py`: script utama

### Masalah / Blocker
Tidak ada

### Saran berikutnya (ke Agent 1)
Script selesai dan berjalan. Suggested next: tambah unit test atau benchmark.
```

### Review Agent 1 & Delegasi Lanjutan:
```
## Review
✅ Script selesai sesuai spesifikasi

## Lanjutan
Task 2: Tambah unit test

delegate_task({
  goal: "Buat test_fibonacci.py dengan pytest/test standalone"
})
```

### Selesai:
```
## Ringkasan Selesai

- Tujuan: Script Python fibonacci ke-N
- Sub-tugas selesai: 2/2
- Output: `fibonacci.py` + `test_fibonacci.py`
- File: fibonacci.py, test_fibonacci.py
- Catatan: Script siap pakai
```

---

## Contoh 2: Review & Refactor Kode

### Trigger User:
```
> Review dan refactor kode di folder ./my-project/src
```

### Respons Agent 1:
```
## Perencanaan

Tujuan: Review kode di ./my-project/src dan refactor jika perlu.

### Checklist Tujuan
- [ ] Review struktur dan quality code
- [ ] Identifikasi issue (bug, performance, readability)
- [ ] Refactor issue yang ditemukan
- [ ] Verifikasi setelah refactor

---

## Delegasi ke Agent 2

### Task 1: Review kode
Review kode di ./my-project/src:
- Identifikasi issue (bug, tech debt, readability)
- Prioritaskan: blocker > performance > style
- Laporkan dalam format laporan Agent 2
```

---

## Contoh 3: Membangun Fitur Project

### Trigger User:
```
> Bangun REST API endpoint untuk user authentication di FastAPI
```

### Respons Agent 1:
```
## Perencanaan

Tujuan: REST API auth endpoint di FastAPI.

### Checklist Tujuan
- [ ] Endpoint POST /auth/register
- [ ] Endpoint POST /auth/login
- [ ] Endpoint POST /auth/refresh
- [ ] Password hashing (bcrypt/argon2)
- [ ] JWT token generation & validation
- [ ] Basic test

---

## Delegasi ke Agent 2

### Task 1: Setup & register endpoint
Buat:
- FastAPI app structure
- POST /auth/register endpoint
- Password hashing
```

---

## Pola Umum

Setiap trigger mengikuti pola:

1. **User memberi instruksi** → Agent 1 terima
2. **Agent 1 merencanakan** → checklist tujuan + sub-tugas
3. **Agent 1 delegasi** → first sub-tugas ke Agent 2
4. **Agent 2 eksekusi & laporkan** → laporan terstruktur
5. **Agent 1 review** → lanjut/revisi/selesai
6. **Ulang** sampai checklist selesai → **Ringkasan ke user**

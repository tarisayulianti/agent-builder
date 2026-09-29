# Plan — Perbaikan Dokumentasi Agent Calling Agent Builder (Gap P1)

**Status:** IN PROGRESS  
**Dibuat:** 2026-09-28  
**Lokasi:** `F:\AI-AGENT\agent-builder\PLAN_FIX.md`  
**Sumber:** Audit dokumentasi menyeluruh (all 13 files in project)

---

## Context

Setelah audit dokumentasi project `agent-builder`, ditemukan 9 gap/keluhan. Dari audit, 4 gap memiliki prioritas TINGGI dan harus diperbaiki sebelum implementasi code (orca.py + hermes_client.py).

Tujuan plan ini: memperbaiki 4 gap HIGH priority agar dokumentasi menjadi stabil dan siap untuk implementasi code.

---

## Goals

1. **Konsistensi mode Agent 2**: Semua dokumen harus konsisten menyebut V1 menggunakan `hermes chat -q`, bukan tmux
2. **Definisi Review Mechanism**: SKILL.md harus memiliki section yang mendefinisikan bagaimana Agent 1 melakukan review output
3. **Spesifikasi Timeout Teknis**: SKILL.md harus memiliki section yang mendefinisikan implementasi teknis timeout (subprocess, bukan workflow)
4. **Klarifikasi CLI dashboard**: IMPLEMENTATION_PLAN.md harus akurat tentang status `bin/agent-builder` (bukan "belum dibuat" yang menyesatkan)

---

## Non-Goals

- Tidak mengubah logika bisnis atau arsitektur yang sudah ditetapkan
- Tidak menambah fitur baru di luar perbaikan gap
- Tidak mengubah V2-V7 roadmap

---

## Tasks

### Task 1: Update `.env.example` — konsistensi mode Agent 2
- Ganti `AGENT2_MODE=tmux` → `AGENT2_MODE=hermes-chat`
- Tambahkan komentar penjelasan: V1 menggunakan hermes chat -q, V2+ bisa pakai tmux

### Task 2: Update `SKILL.md` — tambah section Review Mechanism
- Tambahkan section baru setelah 5b.8 (Failing Cases) atau sebelum section 6
- Isi: kriteria review, langkah review, bagaimana Agent 1 memverifikasi output Agent 2

### Task 3: Update `SKILL.md` — tambah section Technical Timeout Specification
- Tambahkan section teknis tentang timeout: diaplikasikan ke subprocess hermes chat -q, bukan keseluruhan workflow
- Jelaskan timeout 15 menit = 900 detik per subprocess panggilan

### Task 4: Update `SKILL.md` & `AGENT2_INSTRUCTION.md` — klarifikasi mode
- Tambahkan catatan eksplisit: "V1: hermes chat -q (one-shot CLI)", "V2+: hermes chat -q + tmux (opsional)"

### Task 5: Update `IMPLEMENTATION_PLAN.md` — klarifikasi status bin/agent-builder
- Ganti status dari "🔲 Belum dibuat" menjadi "🔲 Plan Ready — CLI wrapper untuk V2 dashboard (V1 tidak perlu)"

---

## Acceptance Criteria

- [ ] `.env.example` tidak lagi menyebut `tmux` sebagai mode default
- [ ] `SKILL.md` memiliki section Review Mechanism yang terdefinisi
- [ ] `SKILL.md` memiliki section Technical Timeout Specification yang terdefinisi
- [ ] `SKILL.md` & `AGENT2_INSTRUCTION.md` konsisten menyebut V1 = hermes chat -q
- [ ] `IMPLEMENTATION_PLAN.md` tidak menyebut `bin/agent-builder` sebagai "belum dibuat" yang menyesatkan

---

## Verification

1. Baca ulang semua file yang diubah, verifikasi perubahan sesuai rencana
2. Cek konsistensi: semua dokumen harus konsisten tentang mode Agent 2 (V1 = hermes chat -q)
3. Cek kelengkapan: Review Mechanism dan Timeout Specification harus ada di SKILL.md

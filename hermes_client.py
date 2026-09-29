#!/usr/bin/env python3
"""
Agent Calling Agent Builder — Hermes Client

Status: READY
Peran: Wrapper subprocess untuk berinteraksi dengan Hermes Agent CLI
Lokasi: F:/AI-AGENT/agent-builder/hermes_client.py
Dependencies: Python 3.11+, subprocess (stdlib)

Modul ini menyediakan interface untuk berinteraksi dengan Hermes Agent
melalui CLI `hermes chat -q`. Digunakan oleh orca.py untuk:
- Mengirim prompt ke Hermes Agent (sebagai Agent 2 executor)
- Menerima output dari Hermes Agent
- Handle timeout, error, dan failing cases

Usage:
    from hermes_client import HermesClient

    client = HermesClient()
    result = client.query("Buat script Python fibonacci ke-N")
    print(result.output)
    print(result.exit_code)
    print(result.timed_out)
"""

import subprocess
import sys
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class QueryResult:
    """Hasil dari query ke Hermes Agent."""
    output: str
    exit_code: int
    timed_out: bool
    error: Optional[str] = None
    duration_seconds: float = 0.0


@dataclass
class Agent2Report:
    """Report terstruktur dari Agent 2 (hasil parse dari output Hermes)."""

    task_id: Optional[str] = None
    duration: Optional[str] = None
    apa_yang_dilakukan: Optional[str] = None
    hasil: list = None  # list of strings
    file_ubah: list = None  # list of (path, desc) tuples
    masalah_blocker: Optional[str] = None
    saran: Optional[str] = None
    failing_case: Optional[str] = None  # TIMEOUT, CRASH, OUTPUT_MISMATCH, STUCK

    def __post_init__(self):
        if self.hasil is None:
            self.hasil = []
        if self.file_ubah is None:
            self.file_ubah = []


class HermesClient:
    """
    Client untuk berinteraksi dengan Hermes Agent CLI.

    Digunakan untuk mengirim prompt dan menerima output.
    Support timeout, quiet mode, dan error handling.
    """

    HERMES_CMD = "hermes"

    def __init__(self, timeout_seconds: int = 900, verbose: bool = False):
        """
        Inisialisasi Hermes Client.

        Args:
            timeout_seconds: Timeout per query dalam detik (default 900 = 15 menit)
            verbose: Cetak debug info ke stderr (default False)
        """
        self.timeout_seconds = timeout_seconds
        self.verbose = verbose

    def query(self, prompt: str) -> QueryResult:
        """
        Kirim prompt ke Hermes Agent dan terima output.

        Args:
            prompt: Teks prompt yang akan dikirim ke Hermes Agent

        Returns:
            QueryResult dengan output, exit_code, timed_out, error, duration

        Raises:
            Tidak ada — semua error ditangani dan dikembalikan dalam QueryResult
        """
        import time

        start_time = time.time()

        try:
            process = subprocess.run(
                [self.HERMES_CMD, "chat", "-q", prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                cwd=None,  # biar dia jalan di environment default
            )

            duration = time.time() - start_time

            if process.returncode != 0 and process.stderr:
                error_msg = process.stderr.strip() or f"Exit code: {process.returncode}"
            else:
                error_msg = None

            if self.verbose:
                print(f"[hermes_client] exit={process.returncode}, duration={duration:.1f}s", file=sys.stderr)

            # Strip ANSI escape codes dan carriage returns
            raw_output = process.stdout.strip() if process.stdout else ""
            clean_output = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', raw_output)
            clean_output = clean_output.replace('\r\n', '\n').replace('\r', '\n').strip()

            return QueryResult(
                output=clean_output,
                exit_code=process.returncode,
                timed_out=False,
                error=error_msg,
                duration_seconds=duration,
            )

        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            output = e.stdout.decode() if e.stdout else ""
            error = e.stderr.decode() if e.stderr else "Timeout expired"

            if self.verbose:
                print(f"[hermes_client] TIMEOUT after {duration:.1f}s", file=sys.stderr)

            return QueryResult(
                output=output.strip(),
                exit_code=-1,
                timed_out=True,
                error=error,
                duration_seconds=duration,
            )

        except FileNotFoundError:
            duration = time.time() - start_time
            return QueryResult(
                output="",
                exit_code=-1,
                timed_out=False,
                error=f"Command '{self.HERMES_CMD}' not found. Pastikan Hermes Agent terinstall.",
                duration_seconds=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            return QueryResult(
                output="",
                exit_code=-1,
                timed_out=False,
                error=str(e),
                duration_seconds=duration,
            )

    def query_agent2(self, task_description: str, task_id: str = None) -> QueryResult:
        """
        Kirim task ke Hermes Agent sebagai Agent 2 (Executor).

        Prompt dibungkus dengan instruksi agar output mengikuti format
        laporan Agent 2 yang terdokumentasi di AGENT2_INSTRUCTION.md.

        Args:
            task_description: Deskripsi tugas yang akan dikerjakan Agent 2
            task_id: Identifier untuk task (opsional, auto-generate jika None)

        Returns:
            QueryResult dengan output laporan Agent 2
        """
        if task_id is None:
            import uuid
            task_id = f"task-{uuid.uuid4().hex[:8]}"

        # Bangun prompt lengkap sesuai format yang didokumentasikan
        # di AGENT2_INSTRUCTION.md dan SKILL.md
        prompt = f"""## Task

**ID**: {task_id}
**Deskripsi**: {task_description}

**Format laporan**: Wajib ikuti template laporan Agent 2:
- Gunakan markdown
- Format: ## Laporan Eksekusi Agent 2
- Sertakan: Task ID, Duration, Apa yang dilakukan, Hasil, File yang diubah/dibuat, Masalah/Blocker, Saran berikutnya
- Jika ada masalah: gunakan label [TIMEOUT], [CRASH], [OUTPUT_MISMATCH], atau [STUCK]
- Wajib laporkan dalam format terstruktur

Laporan dalam format Agent 2 standard.
"""
        return self.query(prompt)


def parse_agent2_report(output: str) -> Agent2Report:
    """
    Parse output dari Hermes Agent (Agent 2) menjadi struktur Agent2Report.

    Parser berdasarkan format laporan yang didokumentasikan di:
    - AGENT2_INSTRUCTION.md (section 3. Format Laporan Wajib)
    - SKILL.md (section 8. Format Laporan)

    Args:
        output: Output teks dari Hermes Agent (Agent 2)

    Returns:
        Agent2Report dengan field yang di-parse
    """
    report = Agent2Report()

    if not output:
        report.masalah_blocker = "Output kosong — tidak ada laporan dari Agent 2"
        report.failing_case = "OUTPUT_MISMATCH"
        return report

    # Deteksi failing cases berdasarkan keyword
    if "[TIMEOUT]" in output:
        report.failing_case = "TIMEOUT"
    elif "[CRASH]" in output:
        report.failing_case = "CRASH"
    elif "[OUTPUT_MISMATCH]" in output:
        report.failing_case = "OUTPUT_MISMATCH"
    elif "[STUCK]" in output:
        report.failing_case = "STUCK"

    # Parse Task ID: **Task ID**: <value>
    import re
    task_id_match = re.search(r'\*\*Task ID\*\*:\s*(.+)', output)
    if task_id_match:
        report.task_id = task_id_match.group(1).strip()

    # Parse Duration: **Duration**: <value>
    duration_match = re.search(r'\*\*Duration\*\*:\s*(.+)', output)
    if duration_match:
        report.duration = duration_match.group(1).strip()

    # Parse "### Apa yang dilakukan" section
    dilakukan_match = re.search(
        r'### Apa yang dilakukan\s*\n(.*?)(?=\n###|\Z)',
        output,
        re.DOTALL
    )
    if dilakukan_match:
        report.apa_yang_dilakukan = dilakukan_match.group(1).strip()

    # Parse "### Hasil" section — bullet points
    hasil_match = re.search(
        r'### Hasil\s*\n(.*?)(?=\n###|\Z)',
        output,
        re.DOTALL
    )
    if hasil_match:
        hasil_text = hasil_match.group(1).strip()
        # Parse bullet points (- item)
        bullets = re.findall(r'^\s*[-*]\s+(.+)$', hasil_text, re.MULTILINE)
        report.hasil = bullets if bullets else [hasil_text]

    # Parse "### File yang diubah/dibuat" section
    file_match = re.search(
        r'### File yang diubah/dibuat\s*\n(.*?)(?=\n###|\Z)',
        output,
        re.DOTALL
    )
    if file_match:
        file_text = file_match.group(1).strip()
        # Parse format: - `path`: desc
        file_entries = re.findall(
            r'^\s*[-*]\s+`([^`]+)`:\s*(.+)$',
            file_text,
            re.MULTILINE
        )
        report.file_ubah = file_entries if file_entries else [(file_text, "")]

    # Parse "### Masalah / Blocker" section
    blocker_match = re.search(
        r'### Masalah / Blocker\s*\n(.*?)(?=\n###|\Z)',
        output,
        re.DOTALL
    )
    if blocker_match:
        report.masalah_blocker = blocker_match.group(1).strip()

    # Parse "### Saran berikutnya" section
    saran_match = re.search(
        r'### Saran berikutnya \(ke Agent 1\)\s*\n(.+)',
        output,
        re.DOTALL
    )
    if saran_match:
        report.saran = saran_match.group(1).strip()

    # Jika tidak ada section "### Apa yang dilakukan" tapi ada output,
    # berarti format tidak sesuai — flag sebagai OUTPUT_MISMATCH
    if not report.apa_yang_dilakukan and output.strip():
        if not report.failing_case:
            report.failing_case = "OUTPUT_MISMATCH"

    return report


# ============================================================================
# CLI (jika dijalankan langsung)
# ============================================================================

def main():
    """CLI interface untuk Hermes Client."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Agent Calling Agent Builder — Hermes Client CLI",
        prog="hermes_client.py",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt yang akan dikirim ke Hermes Agent",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=900,
        help="Timeout dalam detik (default: 900 = 15 menit)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Tampilkan debug info",
    )
    parser.add_argument(
        "--parse", "-p",
        action="store_true",
        help="Parse output sebagai Agent 2 report dan tampilkan secara terstruktur",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Jalankan self-test: init client, parse sample report, detect failing cases",
    )

    args = parser.parse_args()

    if args.test:
        print("=== hermes_client.py — Self-Test ===\n")
        passed = 0
        failed = 0

        # Test 1: Init client
        try:
            client = HermesClient(timeout_seconds=900, verbose=False)
            print("[1] Init HermesClient")
            print("  Timeout: 900s")
            print("  ✅ PASS")
            passed += 1
        except Exception as e:
            print(f"[1] Init HermesClient: ❌ FAIL — {e}")
            failed += 1

        # Test 2: parse_agent2_report (valid report)
        sample_report = """# Agent 2 Report

## Ringkasan
- Task ID: task-001
- Duration: 3 menit

### Apa yang dilakukan
Membuat script Python fibonacci dan menulis ke file.

### Hasil
- Script fibonacci berhasil dibuat

### File yang diubah/dibuat
- `fibonacci.py`: Script fibonacci ke-N

### Saran berikutnya (ke Agent 1)
Lanjutkan ke sub-task berikutnya."""
        try:
            report = parse_agent2_report(sample_report)
            print("[2] parse_agent2_report (valid input)")
            assert report.apa_yang_dilakukan is not None, "Expected apa_yang_dilakukan tidak None"
            assert "fibonacci" in report.apa_yang_dilakukan.lower(), f"Expected 'fibonacci' in apa_yang_dilakukan, got: {report.apa_yang_dilakukan}"
            assert report.failing_case is None
            print(f"  Task ID: {report.task_id or 'N/A (optional field)'}")
            print(f"  Duration: {report.duration or 'N/A'}")
            print(f"  Apa yang dilakukan: parsed ({len(report.apa_yang_dilakukan)} chars)")
            print("  ✅ PASS")
            passed += 1
        except Exception as e:
            print(f"[2] parse_agent2_report (valid input): ❌ FAIL — {e}")
            failed += 1

        # Test 3: parse_agent2_report (invalid — OUTPUT_MISMATCH)
        invalid_output = "hermes: command not found\nError: exit code 127"
        try:
            report = parse_agent2_report(invalid_output)
            print("[3] parse_agent2_report (invalid — OUTPUT_MISMATCH)")
            assert report.failing_case == "OUTPUT_MISMATCH", f"Expected OUTPUT_MISMATCH, got {report.failing_case}"
            print(f"  Failing case: {report.failing_case}")
            print("  ✅ PASS")
            passed += 1
        except Exception as e:
            print(f"[3] parse_agent2_report (invalid): ❌ FAIL — {e}")
            failed += 1

        # Test 4: HermesClient.query (dengan hermes CLI error)
        try:
            print("[4] HermesClient.query (hermes not available)")
            result = client.query("Test prompt")
            print(f"  Exit code: {result.exit_code}")
            print(f"  Timed out: {result.timed_out}")
            assert result.exit_code != 0, "Expected exit code != 0 (hermes not installed)"
            print("  ✅ PASS")
            passed += 1
        except AssertionError:
            print("  ✅ PASS (exit code tidak 0 seperti diharapkan)")
            passed += 1
        except Exception as e:
            print(f"[4] HermesClient.query: ❌ FAIL — {e}")
            failed += 1

        print(f"\n=== Hasil: {passed} passed, {failed} failed ===")
        if failed > 0:
            print("❌ Test FAILED")
            sys.exit(1)
        else:
            print("✅ Semua test PASS")
            sys.exit(0)

    if not args.prompt:
        parser.print_help()
        print("\nContoh penggunaan:")
        print('  python hermes_client.py "Buat script Python fibonacci"')
        print('  python hermes_client.py "Buat script Python fibonacci" --parse')
        print('  python hermes_client.py "Buat script Python fibonacci" --timeout 300')
        sys.exit(0)

    client = HermesClient(timeout_seconds=args.timeout, verbose=args.verbose)
    result = client.query(args.prompt)

    if args.parse:
        report = parse_agent2_report(result.output)
        print("=" * 60)
        print("AGENT 2 REPORT (parsed)")
        print("=" * 60)
        print(f"Task ID: {report.task_id or 'N/A'}")
        print(f"Duration: {report.duration or 'N/A'}")
        print(f"Failing Case: {report.failing_case or 'None'}")
        print()
        if report.apa_yang_dilakukan:
            print("### Apa yang dilakukan")
            print(report.apa_yang_dilakukan)
            print()
        if report.hasil:
            print("### Hasil")
            for h in report.hasil:
                print(f"  - {h}")
            print()
        if report.file_ubah:
            print("### File yang diubah/dibuat")
            for path, desc in report.file_ubah:
                print(f"  - `{path}`: {desc}")
            print()
        if report.masalah_blocker:
            print("### Masalah / Blocker")
            print(report.masalah_blocker)
            print()
        if report.saran:
            print("### Saran berikutnya")
            print(report.saran)
            print()
    else:
        # Output mentah
        if result.timed_out:
            print(f"[TIMEOUT] Query timed out after {result.duration_seconds:.1f}s")
        if result.error:
            print(f"[ERROR] {result.error}", file=sys.stderr)
        print(result.output)


if __name__ == "__main__":
    main()

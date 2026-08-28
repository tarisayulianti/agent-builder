"""Hermes CLI — Termux Proot Edition."""
import os, click
from rich.console import Console
from rich.panel import Panel
from hermes.llm import LLM
from hermes.state import State
from hermes.agents import Recommender, Architect, Planner, Builder, Verifier, Auditor, GitHubAgent

console = Console()

@click.group()
def main():
    """Hermes Agent Builder — Termux Edition"""
    pass

@main.command()
@click.argument("request")
@click.option("--option", "-o", default=0, help="Pilih opsi 1-3 (0 = manual)")
@click.option("--github", "-g", default="", help="GitHub repo URL (opsional)")
def build(request, option, github):
    """Build project dari ide."""
    try:
        llm = LLM()
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return

    state = State()
    state.set("request", request)

    # Phase 1: Recommend
    console.print("\n[blue]Phase 1:[/blue] Generate 3 opsi...")
    rec = Recommender(llm, state)
    ideas = rec.run(request)
    if not ideas:
        console.print("[red]Gagal generate ide.[/red]")
        return

    for i, idea in enumerate(ideas[:3], 1):
        name = idea.get("name", f"Opsi {i}")
        stack = ", ".join(idea.get("stack", [])[:3])
        console.print(f"  {i}. {name} ({stack})")

    if option == 0:
        choice = console.input("\nPilih opsi (1-3): ").strip()
        idx = int(choice) - 1 if choice.isdigit() else 0
    else:
        idx = option - 1
    idx = max(0, min(idx, len(ideas) - 1))
    selected = ideas[idx]
    state.set("selected", selected)
    console.print(f"[green]Selected: {selected.get('name', 'Unknown')}[/green]")

    # Phase 2: Architect
    console.print("\n[blue]Phase 2:[/blue] Design arsitektur...")
    arch = Architect(llm, state)
    architecture = arch.run(selected)

    # Phase 3: Plan
    console.print("[blue]Phase 3:[/blue] Rancang file structure...")
    planner = Planner(llm, state)
    plan = planner.run(architecture)

    # Phase 4: Build
    console.print("[blue]Phase 4:[/blue] Nulis kode...")
    builder = Builder(llm, state)
    code = builder.run(plan)

    # Phase 5: Verify
    console.print("[blue]Phase 5:[/blue] Verifikasi kode...")
    verifier = Verifier(llm, state)
    v = verifier.run(code)
    if v["status"] == "FAIL":
        console.print(f"[yellow]Warning: {len(v['issues'])} issue ditemukan[/yellow]")
        for issue in v["issues"]:
            console.print(f"  - {issue}")
    else:
        console.print("[green]Verifikasi PASS[/green]")

    # Phase 6: Audit
    console.print("[blue]Phase 6:[/blue] Audit keamanan...")
    auditor = Auditor(llm, state)
    a = auditor.run(code)
    console.print(f"[green]Audit Score: {a['score']}/100[/green]")
    for f in a["findings"]:
        console.print(f"  [yellow]{f['file']}: {f['issue']}[/yellow]")

    # Phase 7: Git
    console.print("[blue]Phase 7:[/blue] Commit ke git...")
    git = GitHubAgent(llm, state)
    g = git.run(code, github)

    # Final
    console.print("\n" + "=" * 40)
    console.print("[bold green]HERMES BUILD COMPLETE[/bold green]")
    console.print(f"Output: {code['output_dir']}")
    console.print(f"Files: {len(code['files'])}")
    console.print(f"Audit: {a['score']}/100")
    console.print(f"Git: {g['local_path']}")
    console.print("=" * 40)

if __name__ == "__main__":
    main()

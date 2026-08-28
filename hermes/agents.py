"""Semua agent di 1 file. Simple."""
import json, os, re
from pathlib import Path
from hermes.llm import LLM
from hermes.state import State

class BaseAgent:
    def __init__(self, llm: LLM, state: State):
        self.llm = llm
        self.state = state

    def ask(self, prompt, system="", temp=0.3):
        return self.llm.chat(prompt, system=system, temp=temp)

    def parse_json(self, text):
        try:
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
        except:
            return {}

class Recommender(BaseAgent):
    def run(self, request):
        system = "Kamu adalah Recommender. Berikan 3 opsi solusi dalam format JSON."
        prompt = f"User minta: {request}\n\nBerikan 3 opsi solusi teknis terbaik (2026) dalam JSON:\n{{\"options\": [{{\"name\":\"...\",\"stack\":[],\"pros\":[],\"cons\":[],\"complexity\":\"Low/Medium/High\"}}]}}"
        r = self.ask(prompt, system, temp=0.7)
        data = self.parse_json(r)
        self.state.set("ideas", data.get("options", []))
        return data.get("options", [])

class Architect(BaseAgent):
    def run(self, idea):
        system = "Kamu adalah Architect. Desain arsitektur teknis."
        prompt = f"Idea: {json.dumps(idea)}\n\nDesain arsitektur lengkap (stack, database, API) dalam JSON."
        r = self.ask(prompt, system, temp=0.2)
        data = self.parse_json(r)
        self.state.set("architecture", data)
        return data

class Planner(BaseAgent):
    def run(self, arch):
        system = "Kamu adalah Planner. Rancang struktur file."
        prompt = f"Arsitektur: {json.dumps(arch)}\n\nBuat daftar file & fungsi dalam JSON:\n{{\"files\": [{{\"path\":\"...\",\"purpose\":\"...\",\"functions\":[]}}]}}"
        r = self.ask(prompt, system, temp=0.2)
        data = self.parse_json(r)
        self.state.set("plan", data)
        return data

class Builder(BaseAgent):
    def run(self, plan):
        files = plan.get("files", [])
        out = Path("output/generated")
        out.mkdir(parents=True, exist_ok=True)
        written = []
        for fspec in files:
            path = fspec.get("path", "file.py")
            purpose = fspec.get("purpose", "")
            funcs = fspec.get("functions", [])
            system = "Kamu adalah Senior Developer. Tulis kode LENGKAP, NO placeholder, NO TODO. Production ready."
            prompt = f"File: {path}\nPurpose: {purpose}\nFunctions: {json.dumps(funcs)}\n\nTulis kode lengkap untuk file ini. Langsung kode saja, tanpa penjelasan."
            code = self.ask(prompt, system, temp=0.1)
            # Bersihin markdown
            if "```" in code:
                lines = code.split("\n")
                in_code = False
                clean = []
                for line in lines:
                    if line.startswith("```"):
                        in_code = not in_code
                        continue
                    if in_code:
                        clean.append(line)
                code = "\n".join(clean) if clean else code
            full = out / path
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(code)
            written.append(path)
        self.state.set("code", {"output_dir": str(out), "files": written})
        return {"output_dir": str(out), "files": written}

class Verifier(BaseAgent):
    def run(self, code_result):
        out = Path(code_result.get("output_dir", "output/generated"))
        files = code_result.get("files", [])
        ok = True
        issues = []
        for fname in files:
            fpath = out / fname
            if not fpath.exists():
                ok = False
                issues.append(f"{fname}: ga ada")
                continue
            content = fpath.read_text()
            # Cek stub
            stubs = ["TODO", "FIXME", "NotImplementedError", "pass  #", "...  #"]
            for s in stubs:
                if s.lower() in content.lower():
                    issues.append(f"{fname}: ada stub ({s})")
            # Cek syntax python
            if fname.endswith(".py"):
                try:
                    compile(content, fname, "exec")
                except SyntaxError as e:
                    ok = False
                    issues.append(f"{fname}: syntax error line {e.lineno}")
        result = {"status": "PASS" if ok and not issues else "FAIL", "issues": issues}
        self.state.set("verification", result)
        return result

class Auditor(BaseAgent):
    def run(self, code_result):
        out = Path(code_result.get("output_dir", "output/generated"))
        findings = []
        for fname in code_result.get("files", []):
            fpath = out / fname
            if not fpath.exists():
                continue
            content = fpath.read_text()
            # Cek hardcoded secret
            if re.search(r'(password|secret|token|api_key)\s*=\s*["\'][^"\']+["\']', content, re.I):
                findings.append({"file": fname, "issue": "Hardcoded secret", "fix": "Pake env var"})
            # Cek eval
            if "eval(" in content:
                findings.append({"file": fname, "issue": "eval() detected", "fix": "Hapus eval"})
        score = 100 - len(findings) * 10
        result = {"score": max(0, score), "findings": findings}
        self.state.set("audit", result)
        return result

class GitHubAgent(BaseAgent):
    def run(self, code_result, repo_url=""):
        from git import Repo
        out = Path(code_result.get("output_dir", "output/generated"))
        repo = Repo.init(out)
        gitignore = out / ".gitignore"
        gitignore.write_text("__pycache__/\n*.pyc\n.env\n")
        repo.git.add(A=True)
        repo.index.commit("feat: initial commit by Hermes")
        if repo_url:
            # Push logic (simplified)
            pass
        return {"local_path": str(out), "commit": str(repo.head.commit.hexsha)}

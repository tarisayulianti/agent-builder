# Hermes Agent — Termux Proot Edition

## Install (Termux Ubuntu Proot)

```bash
cd ~/hermes-termux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Run

```bash
source venv/bin/activate
export OPENAI_API_KEY="sk-..."
hermes build "Bikin REST API todo list"
```

## Note
- Minimal dependency, no conflict
- OpenAI only (gpt-4o-mini default, bisa ganti via env)
- Output di folder `output/generated/`

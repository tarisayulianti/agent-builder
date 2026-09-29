#!/usr/bin/env bash
# One-shot installer for Agent Builder
# Works on Windows Git-Bash / MSYS2 / Termux / Linux / macOS
set -e

echo "🚀 Agent Builder — One-Shot Installer"
echo ""

# 1. Check Python
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" &>/dev/null; then
    PYTHON="python"
fi
echo "✅ Python: $($PYTHON --version 2>&1)"

# 2. Clone repo (if not already present)
if [ ! -d "agent-builder" ]; then
    echo "📥 Cloning agent-builder..."
    git clone -b master https://github.com/tarisayulianti/agent-builder.git
fi
cd agent-builder
echo "📁 Working dir: $(pwd)"

# 3. Virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating venv..."
    "$PYTHON" -m venv venv
fi

# Activate (cross-platform)
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
fi
echo "✅ Venv activated: $(which python)"

# 4. Install dependencies
echo "📦 Installing dependencies..."
python -m pip install --upgrade pip -q 2>/dev/null || true
python -m pip install -r requirements.txt -q
python -m pip install -e . -q
echo "✅ Dependencies installed"

# 5. Verify hermes CLI
echo ""
echo "🔍 Checking Hermes CLI..."
if hermes --version &>/dev/null; then
    echo "✅ Hermes CLI: $(hermes --version 2>&1)"
    echo ""
    echo "🔧 Setup model (jika belum pernah):"
    echo "   hermes setup --model-setup --interactive"
else
    echo "⚠️  Hermes CLI tidak ditemukan."
    echo "   Install: https://hermes-agent.nousresearch.com/docs"
    echo ""
    echo "📝 Catatan: hermes_client.py tetap bisa di-test tanpa hermes:"
    python hermes_client.py --test
fi

# 6. Run tests
echo ""
echo "🧪 Running self-tests..."
python status_tracker.py --test
python hermes_client.py --test
echo ""
echo "🎉 Install complete!"
echo ""
echo "Langkah selanjutnya:"
echo "  1. Jika hermes belum login: hermes setup --model-setup --interactive"
echo "  2. Test: python orca.py run \"buat script python fibonacci\" --verbose"

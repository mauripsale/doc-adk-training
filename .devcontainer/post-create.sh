#!/usr/bin/env bash
set -e

echo "🚀 [ADK DevContainer] Setting up your Zero-Setup development environment..."

# 1. Ensure uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# 2. Persist PATH and aliases to shell profiles
for profile in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$profile" ]; then
        if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$profile"; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$profile"
        fi
        if ! grep -q 'alias grade=' "$profile"; then
            echo 'alias grade="python3 /workspace/scripts/grade_lab.py"' >> "$profile"
        fi
    fi
done

# 3. Create virtual environment
WORKSPACE_DIR="$(pwd)"
echo "🐍 Creating virtual environment at ${WORKSPACE_DIR}/.venv..."
uv venv "${WORKSPACE_DIR}/.venv"

# 4. Install training dependencies
echo "📚 Installing course dependencies from requirements-dev.txt..."
uv pip install --python "${WORKSPACE_DIR}/.venv/bin/python" -r requirements-dev.txt

# 5. Initialize .env from .env.example if missing
if [ ! -f .env ] && [ -f .env.example ]; then
    echo "📝 Initializing .env template..."
    cp .env.example .env
fi

# 6. Welcome Banner
echo ""
echo "================================================================================"
echo "🎓 Google ADK Training (From Zero to Hero) - DevContainer Ready!"
echo "================================================================================"
echo "✨ Python Environment: ${WORKSPACE_DIR}/.venv (Activated by default)"
echo "🔑 Next Step - Configure your credentials in .env:"
echo "   - Option 1 (AI Studio): Add your GOOGLE_API_KEY to .env"
echo "   - Option 2 (Vertex AI): Run 'gcloud auth application-default login'"
echo ""
echo "🧪 Test and Grade your progress:"
echo "   grade                          # Grade current module lab"
echo "   grade --all                    # Run full curriculum test suite"
echo "   python scripts/test_solutions.py --ignore-missing-optional"
echo "================================================================================"
echo ""

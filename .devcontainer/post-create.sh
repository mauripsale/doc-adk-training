#!/usr/bin/env bash
set -e

echo "🚀 [ADK DevContainer] Setting up your Zero-Setup development environment..."

WORKSPACE_DIR="$(pwd)"

# 1. Ensure uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

mkdir -p "$HOME/.local/bin"

# 2. Create standalone executable `grade` script
cat << 'EOF' > "$HOME/.local/bin/grade"
#!/usr/bin/env bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
if [ -f "${REPO_ROOT}/.venv/bin/python" ] && [ -f "${REPO_ROOT}/scripts/grade_lab.py" ]; then
    exec "${REPO_ROOT}/.venv/bin/python" "${REPO_ROOT}/scripts/grade_lab.py" "$@"
elif [ -f "${REPO_ROOT}/scripts/grade_lab.py" ]; then
    exec python3 "${REPO_ROOT}/scripts/grade_lab.py" "$@"
else
    echo "❌ Error: Could not locate scripts/grade_lab.py in repository root."
    exit 1
fi
EOF
chmod +x "$HOME/.local/bin/grade"

# 3. Create virtual environment
echo "🐍 Creating virtual environment at ${WORKSPACE_DIR}/.venv..."
uv venv "${WORKSPACE_DIR}/.venv"

# 4. Install training dependencies
echo "📚 Installing course dependencies from requirements-dev.txt..."
uv pip install --python "${WORKSPACE_DIR}/.venv/bin/python" -r requirements-dev.txt

# 5. Persist PATH and virtual environment activation to shell profiles
for profile in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$profile" ]; then
        if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$profile"; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$profile"
        fi
        if ! grep -q 'source "${WORKSPACE_DIR}/.venv/bin/activate"' "$profile" && ! grep -q '.venv/bin/activate' "$profile"; then
            echo "[ -f \"${WORKSPACE_DIR}/.venv/bin/activate\" ] && source \"${WORKSPACE_DIR}/.venv/bin/activate\"" >> "$profile"
        fi
    fi
done

# 6. Initialize .env from .env.example if missing
if [ ! -f .env ] && [ -f .env.example ]; then
    echo "📝 Initializing .env template..."
    cp .env.example .env
fi

# 7. Welcome Banner
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

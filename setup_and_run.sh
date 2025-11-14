#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/TraCR-National-UTC/TraCR-RAG.git"
REPO_DIR="TraCR-RAG"

echo "==> Checking prerequisites (Python 3.10+, Git) ..."
command -v git >/dev/null 2>&1 || { echo "Git not found. Install Git from https://git-scm.com/downloads and rerun."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python3 not found. Install from https://www.python.org/downloads/ and rerun."; exit 1; }

python3 - <<'PYVERCHK'
import sys
maj, min = sys.version_info[:2]
if not (maj > 3 or (maj == 3 and min >= 10)):
    print("❌ Python 3.10+ required. You have", sys.version)
    sys.exit(1)
PYVERCHK

echo "==> Cloning or updating repository ..."
if [ -d "$REPO_DIR/.git" ]; then
  git -C "$REPO_DIR" pull --ff-only
else
  git clone "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

echo "==> Creating virtual environment ..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Upgrading pip and installing dependencies ..."
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  echo "⚠️  requirements.txt not found — skipping dependency install."
fi

# Create dummy .env file
if [ ! -f .env ]; then
  echo "==> Creating .env with placeholder OpenAI API key ..."
  cat > .env <<'EOF'
# --- Django settings ---
ALLOWED_HOSTS=localhost,127.0.0.1

# --- OpenAI configuration ---
# Replace this dummy key with your actual OpenAI API key (starts with "sk-")
OPENAI_API_KEY=sk-REPLACE_WITH_YOUR_KEY
EOF
fi

echo "✅ Setup complete!"
echo
echo "Next steps:"
echo "1️⃣  Open the file '$PWD/.env' in any text editor"
echo "2️⃣  Replace 'sk-REPLACE_WITH_YOUR_KEY' with your real OpenAI API key"
echo "3️⃣  Save the file"
echo "4️⃣  To run the app again later:"
echo "      source .venv/bin/activate && python manage.py runserver"
echo
echo "==> Starting development server ..."
if [ -f manage.py ]; then
  python manage.py runserver
else
  echo "⚠️  manage.py not found — please run manually inside project folder."
fi

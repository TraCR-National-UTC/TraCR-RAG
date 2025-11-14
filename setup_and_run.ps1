# setup_and_run.ps1
$ErrorActionPreference = "Stop"

$repoUrl = "https://github.com/TraCR-National-UTC/TraCR-RAG.git"
$repoDir = "TraCR-RAG"

Write-Host "==> Checking prerequisites (Python 3.10+, Git) ..."
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Error "Git not found. Install from https://git-scm.com/downloads and rerun."
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Error "Python not found. Install from https://www.python.org/downloads/ and rerun."
}

# Version check
& python - << 'PYCHK'
import sys
maj,min=sys.version_info[:2]
sys.exit(0 if (maj>3 or (maj==3 and min>=10)) else 1)
PYCHK
if ($LASTEXITCODE -ne 0) { throw "Python 3.10+ required; please upgrade." }

Write-Host "==> Cloning or updating repository ..."
if (Test-Path "$repoDir/.git") {
  git -C "$repoDir" pull --ff-only
} else {
  git clone $repoUrl $repoDir
}

Set-Location $repoDir

Write-Host "==> Creating virtual environment ..."
python -m venv .venv
. ".\.venv\Scripts\Activate.ps1"

Write-Host "==> Upgrading pip and installing dependencies ..."
python -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
  pip install -r requirements.txt
} else {
  Write-Warning "requirements.txt not found — skipping dependency install."
}

if (-not (Test-Path ".env")) {
  Write-Host "==> Creating .env with placeholder OpenAI API key ..."
  @"
# --- Django settings ---
ALLOWED_HOSTS=localhost,127.0.0.1

# --- OpenAI configuration ---
# Replace this dummy key with your actual OpenAI API key (starts with 'sk-')
OPENAI_API_KEY=sk-REPLACE_WITH_YOUR_KEY
"@ | Out-File -Encoding UTF8 ".env"
}

Write-Host "✅ Setup complete!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1️⃣  Open the file '.env' in Notepad"
Write-Host "2️⃣  Replace 'sk-REPLACE_WITH_YOUR_KEY' with your real OpenAI API key"
Write-Host "3️⃣  Save and close the file"
Write-Host "4️⃣  To run the app later, open PowerShell and run:"
Write-Host "       .\.venv\Scripts\Activate.ps1"
Write-Host "       python manage.py runserver"
Write-Host ""
Write-Host "==> Starting development server ..."
if (Test-Path "manage.py") {
  python manage.py runserver
} else {
  Write-Warning "manage.py not found — please run manually."
}

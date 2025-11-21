@echo off
@setlocal enableextensions  
cd /d "%~dp0"

py --version
git --version

cd /d "%~dp0"

if not exist "TraCR-RAG" (
	echo Cloning TraCR-RAG repository from GitHub
	git clone https://github.com/TraCR-National-UTC/TraCR-RAG.git
	echo TraCR-RAG repository from GitHub successfully cloned.
) else (
	echo TraCR-RAG repository from GitHub already present. 
)


cd "TraCR-RAG"

if not exist .venv (
	py -3.12 -m venv .venv
	echo virtual environment created as .venv
) else (
	echo virtual environment exists as .venv
)

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
call .\.venv\Scripts\activate.bat

Rem Make sure pip is up to date
pip install --upgrade pip

Rem Install everything listed in requirements.txt
pip install -r requirements.txt

REM --- Create .env file and write variables ---
echo ALLOWED_HOSTS=localhost,127.0.0.1> .env
echo OPENAI_API_KEY=sk-your-key-here>> .env

if %errorlevel% neq 0 (
    echo ERROR: Command failed with exit code %errorlevel%.
    pause
    exit /b %errorlevel%
)

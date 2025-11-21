cd /d "%~dp0"
git pull

powershell -Command "Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force"
call .\.venv\Scripts\activate.bat

pip install --upgrade pip
pip install -r requirements.txt
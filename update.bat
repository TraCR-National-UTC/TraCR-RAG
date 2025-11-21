cd /d "%~dp0"
git pull

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
call .\.venv\Scripts\activate.bat

pip install --upgrade pip
pip install -r requirements.txt
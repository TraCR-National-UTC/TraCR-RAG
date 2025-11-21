cd /d "%~dp0"
git pull

powershell -Command "Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force"
call .\.venv\Scripts\activate.bat

python manage.py collectstatic --noinput

python manage.py runserver
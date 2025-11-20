cd /d "%~dp0"
git pull

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
call .\.venv\Scripts\activate.bat

python manage.py collectstatic --noinput

python manage.py runserver
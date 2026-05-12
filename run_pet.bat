@echo off
set SCRIPT_DIR=%~dp0
call "%SCRIPT_DIR%\.venv\Scripts\activate"
python "%SCRIPT_DIR%desktop_pet_app.py"
pause

@echo off
echo Starting HoneyBadger Pro Server...
echo.
echo Server will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server.
echo ================================================
echo.

cd /d "%~dp0"
call backend\venv\Scripts\activate.bat
cd backend
python main.py

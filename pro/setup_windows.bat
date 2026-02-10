@echo off
echo ================================================
echo   HoneyBadger Pro - Local Server Setup
echo ================================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM Check for PostgreSQL
echo Checking for PostgreSQL...
where psql >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: PostgreSQL not found in PATH.
    echo Make sure PostgreSQL is installed and running.
    echo.
    echo Download from: https://www.postgresql.org/download/windows/
    echo.
    pause
)

REM Create virtual environment
if not exist "pro\backend\venv" (
    echo Creating virtual environment...
    python -m venv pro\backend\venv
)

REM Activate and install dependencies
echo Installing dependencies...
call pro\backend\venv\Scripts\activate.bat
pip install -r pro\backend\requirements.txt

REM Create database (if psql is available)
echo.
echo ================================================
echo   DATABASE SETUP
echo ================================================
echo.
echo If PostgreSQL is installed, run these commands:
echo.
echo   psql -U postgres
echo   CREATE DATABASE honeybadger;
echo   CREATE USER honeybadger WITH PASSWORD 'honeybadger';
echo   GRANT ALL PRIVILEGES ON DATABASE honeybadger TO honeybadger;
echo   \q
echo.
echo Or edit pro\backend\config.py with your database URL.
echo ================================================
echo.

pause

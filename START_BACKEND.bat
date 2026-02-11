@echo off
REM VoicePulse AI - Quick Start Script
REM This script starts the backend server

echo ============================================
echo   VoicePulse AI - Starting Backend Server
echo ============================================
echo.

cd /d "%~dp0backend"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo Checking Python installation...
"%PYTHON_EXE%" --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo.
echo Starting backend server...
echo Server will run on: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

"%PYTHON_EXE%" -m waitress --listen=0.0.0.0:5000 app:app

pause

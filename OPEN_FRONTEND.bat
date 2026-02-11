@echo off
REM VoicePulse AI - Open Frontend
REM This script opens the frontend in your default browser

echo ============================================
echo   VoicePulse AI - Opening Frontend
echo ============================================
echo.

cd /d "%~dp0frontend"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
	set "PYTHON_EXE=python"
)

echo Opening VoicePulse AI in your default browser...
echo.
echo Make sure the backend server is running!
echo If not, run START_BACKEND.bat first
echo.

"%PYTHON_EXE%" --version >nul 2>&1
if errorlevel 1 (
	start index.html
) else (
	start "VoicePulse Frontend" "%PYTHON_EXE%" -m http.server 8000
	timeout /t 1 >nul
	start http://localhost:8000/index.html
)

echo.
echo Frontend opened successfully!
echo ============================================
pause

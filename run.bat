@echo off
setlocal enabledelayedexpansion

echo =======================================================================
echo  SCSS SATYA — Forensic Image Authenticity Screening Platform
echo  Guiding Doctrine: "The tool screens. The expert decides."
echo =======================================================================

cd /d "%~dp0"

:: Check virtual environment
if not exist "backend\.venv\Scripts\python.exe" (
    echo [SETUP] Initializing Python virtual environment...
    python -m venv backend\.venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Ensure Python 3.11+ is installed.
        pause
        exit /b 1
    )
    echo [SETUP] Installing backend dependencies...
    backend\.venv\Scripts\pip.exe install -r backend\requirements.txt
)

:: Check frontend production build
if not exist "frontend\dist\index.html" (
    echo [SETUP] Building frontend SPA production assets...
    cd frontend
    call npm install
    call npm run build
    cd ..
)

:: Run unified server
echo [LAUNCH] Starting unified SCSS SATYA server...
backend\.venv\Scripts\python.exe scripts\run_backend.py

pause

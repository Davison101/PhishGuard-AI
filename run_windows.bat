@echo off
setlocal
cd /d "%~dp0"
title PhishGuard AI - Local URL Scanner

echo ========================================================
echo    PhishGuard AI - Phishing URL Classifier
echo ========================================================
echo.

REM Prefer Python 3.11 where the Windows Python launcher is available.
py -3.11 --version >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3.11"
) else (
    set "PYTHON_CMD=python"
)

%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo Python was not found.
    echo Install Python 3.11 from https://www.python.org/downloads/release/python-3119/
    echo During setup, check the box that adds Python to PATH.
    echo Then double-click this file again.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating the app's private Python environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto failed
    echo.
    echo [2/3] Installing packages. This can take a while the first time...
    call ".venv\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 goto failed
    call ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto failed
) else (
    echo Existing Python environment found.
)

echo.
echo [3/3] Starting PhishGuard AI...
echo When the app opens, use the URL shown in the terminal (normally http://localhost:8501).
echo The first run downloads the AI model and requires internet access.
echo Keep this window open while using the app. Press Ctrl+C here to stop it.
echo.
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto failed
exit /b 0

:failed
echo.
echo Setup or launch failed. Read the error above. Check Python and internet access, then try again.
pause
exit /b 1

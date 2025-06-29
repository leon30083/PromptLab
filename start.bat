@echo off
cd /d "%~dp0"

echo.
echo ================================================
echo    PromptLab Quick Start
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found, please install Python 3.8+
    pause
    exit /b 1
)
echo Python found

REM Activate virtual environment if exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Using system Python
)

REM Install dependencies quickly
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt --quiet --disable-pip-version-check
)

REM Start server directly
echo.
echo Starting PromptLab server...
echo Note: MLflow will start automatically if needed
echo.
python enhanced_promptlab_server.py

echo.
echo Server stopped
pause
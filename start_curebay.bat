@echo off
:: ============================================================
:: start_curebay.bat — One-Click CureBay Launcher for Windows
:: ============================================================
:: Double-click this file to:
::   1. Check System and Python Version Requirements
::   2. Install Python Dependencies
::   3. Verify Local AI models (MedGemma)
::   4. Start the CureBay backend server
:: ============================================================

title CureBay AI Health Assistant

echo.
echo  =========================================================
echo    CureBay AI Health Assistant — Starting...
echo  =========================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python is not installed or not on PATH.
    echo.
    echo  Please install Python 3.10+ from https://python.org/downloads
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Show Python version
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  Python: %%v
echo.

:: Run the setup script
echo  Running setup... (this may take a while on first run)
echo.
python "%~dp0setup.py"

:: If setup.py exits (e.g. Ctrl+C), just pause before closing
echo.
echo  Server stopped.
pause

@echo off
echo ========================================
echo   🚚 Delivery Route Optimization System
echo ========================================
echo.
echo Starting the application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js 14+ from https://nodejs.org
    pause
    exit /b 1
)

echo ✅ Python and Node.js found
echo.

REM Start the application
echo 🚀 Starting both backends...
python start_application.py

echo.
echo ========================================
echo   Application stopped
echo ========================================
pause 
@echo off
title MAHFOOZ Restaurant - Server Launcher
color 06

echo ========================================================
echo    MAHFOOZ RESTAURANT - LOCAL SERVER LAUNCHER
echo    Location: Patna, Bihar, India
echo ========================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking dependencies and installing required packages...
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Pip encountered an issue, attempting with 'python'...
    python -m pip install -r requirements.txt
)

echo.
echo [2/3] Checking and initializing database & sample dishes...
py seed_data.py
if %errorlevel% neq 0 (
    python seed_data.py
)

echo.
echo [3/3] Starting MAHFOOZ Restaurant Server...
echo.
echo ========================================================
echo   * Customer Website: http://127.0.0.1:5000
echo   * Admin Dashboard:  http://127.0.0.1:5000/admin/login
echo   * Admin Username:   admin
echo   * Admin Password:   admin123
echo ========================================================
echo.
echo Press Ctrl + C to stop the server anytime.
echo.

py app.py
if %errorlevel% neq 0 (
    python app.py
)

pause

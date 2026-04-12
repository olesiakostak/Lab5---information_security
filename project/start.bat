@echo off

cd /d "%~dp0"

echo ========================================================
echo        STARTING LAB WORK 
echo ========================================================
echo.


echo [*] Checking libraries...
pip install streamlit pandas > nul 2>&1

if %errorlevel% neq 0 (
    echo [!] Warning: Could not install libraries automatically.
    echo     Please ensure Python is installed and added to PATH.
) else (
    echo [+] Libraries are ready.
)

echo.
echo [*] Launching Streamlit App...
echo.

streamlit run app.py

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] The application crashed! See details above.
)

pause
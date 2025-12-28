@echo off
echo Starting Piano Tuner...
cd /d "%~dp0"

echo Checking and installing dependencies...
py -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Starting server...
py app.py
pause

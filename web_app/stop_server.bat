@echo off
echo Stopping Piano Tuner Server...
taskkill /F /IM python.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Server stopped successfully!
) else (
    echo No server running.
)
pause

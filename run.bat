@echo off
chcp 65001 >nul
cd /d "%~dp0"
python yt_monitor.py
echo.
pause

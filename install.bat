@echo off
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 "%~dp0install.py" %*
) else (
    python "%~dp0install.py" %*
)

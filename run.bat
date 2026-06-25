@echo off
REM ====================================================================
REM  ttsGdocs LAUNCHER (run.bat)
REM ====================================================================
REM  Ensures UTF-8 (chcp 65001) so the themed preflight renders Nerd Font
REM  icons and box characters correctly, runs diagnostics, then starts the
REM  local Python TTS backend.
REM ====================================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"

REM --- Configuration ---
set LAUNCH_CMD=python backend\server.py
REM ---------------------

REM Themed preflight checks (Python version, TTS engines, port) if Python exists
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
  if exist "%~dp0launcher\preflight.py" (
    python "%~dp0launcher\preflight.py"
  )
)

echo.
echo Launching ttsGdocs backend...
echo ----------------------------------------------------
call %LAUNCH_CMD% %*
set EXITCODE=%ERRORLEVEL%
echo ----------------------------------------------------

if not "%EXITCODE%"=="0" (
  echo.
  echo  [!] Backend stopped with exit code %EXITCODE%.
  pause
)
endlocal

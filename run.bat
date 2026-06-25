@echo off
REM Launch the TTS backend - keeps the repo root clean.
python "%~dp0backend\server.py" %*

"""Central configuration for the Docs -> Speech TTS backend.

Every path is resolved from THIS file's location, so the server works no
matter which directory you launch it from (per the project's run wrappers).
"""
from pathlib import Path

# backend/ directory (this file lives in it)
BACKEND_DIR = Path(__file__).resolve().parent
# repo root (one level up from backend/)
REPO_ROOT = BACKEND_DIR.parent

# Where generated audio files are written.
OUTPUT_DIR = BACKEND_DIR / "output"

# Server bind address. 127.0.0.1 keeps it local-only; the browser extension
# is the only thing that talks to it.
HOST = "127.0.0.1"
PORT = 5000

# Preferred TTS engine order. The first importable/working engine wins.
#   "pyttsx3" = offline (no network)
#   "gtts"    = online (Google, needs internet)
ENGINE_PRIORITY = ["pyttsx3", "gtts"]

# Default voice settings (engine-dependent; safely ignored if unsupported).
DEFAULT_RATE = 175      # words per minute (pyttsx3)
DEFAULT_LANG = "en"     # language code (gtts)

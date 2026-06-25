#!/usr/bin/env python3
"""preflight.py - themed startup diagnostics for ttsGdocs.

Uses launcher/ui_theme.py (zero required dependencies) to print a banner and
check the environment before the backend starts:
  * Python version
  * which TTS engines are importable (pyttsx3 / gTTS)
  * whether the target port is free

Purely informational and never fatal. run.sh / run.bat call this, then launch
backend/server.py.
"""
import importlib.util
import os
import socket
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)                              # ui_theme.py lives here
sys.path.insert(0, os.path.join(ROOT, "backend"))    # to read config defaults

import ui_theme

try:
    import config
    HOST = getattr(config, "HOST", "127.0.0.1")
    PORT = int(getattr(config, "PORT", 5000))
except Exception:
    HOST, PORT = "127.0.0.1", 5000


def _port_free(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.4)
            return s.connect_ex((host, port)) != 0
    except Exception:
        return True


def main():
    ui_theme.print_banner("ttsGdocs", "Google Docs -> downloadable speech")
    ui_theme.print_rule("preflight")

    v = sys.version_info
    ui_theme.print_check("pass" if v >= (3, 8) else "fail",
                         "Python version",
                         "%d.%d.%d" % (v.major, v.minor, v.micro))

    engines = []
    for mod, label in (("pyttsx3", "pyttsx3 (offline)"), ("gtts", "gTTS (online)")):
        present = importlib.util.find_spec(mod) is not None
        ui_theme.print_check("pass" if present else "warn",
                             "Engine: " + label,
                             "ready" if present else "pip install " + mod)
        if present:
            engines.append(mod)

    if not engines:
        ui_theme.print_check("fail", "TTS engines",
                             "none found -> POST /tts will return 503")

    free = _port_free(HOST, PORT)
    ui_theme.print_check("pass" if free else "warn",
                         "Port %d" % PORT,
                         "available" if free else "in use (stop the other process)")

    ui_theme.print_rule()
    url = "http://%s:%d" % (HOST, PORT)
    if engines:
        ui_theme.print_server_online(url, os.path.join(ROOT, "backend", "output"),
                                     title="WILL SERVE AT")
    else:
        ui_theme.panel(
            [ui_theme.icon("warn") + "  Install an engine:  "
             + ui_theme.colorize("pip install -r backend/requirements.txt", "#00e5ff")],
            title="NO TTS ENGINE", border_hex="#ffcc00")


if __name__ == "__main__":
    main()

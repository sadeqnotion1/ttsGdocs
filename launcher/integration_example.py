"""
integration_example.py - how to wire ui_theme into an EXISTING launcher/doctor
with minimal, additive edits. This mirrors a typical MyProject-style setup
(main.py + doctor.py + a server 'online' banner).

These are illustrative snippets, not a runnable file on their own.
"""

# --------------------------------------------------------------------------- #
# 1) At the TOP of your launcher entry point (e.g. backend/main.py)
# --------------------------------------------------------------------------- #
#
#   import ui_theme
#   ui_theme.print_banner("MyProject", "A generic description of my project features")
#


# --------------------------------------------------------------------------- #
# 2) In your doctor / preflight check printer (e.g. frontend/doctor.py)
#    Replace the old plain print with print_check. Map your existing
#    PASS / WARN / FAIL labels to "pass" / "warn" / "fail".
# --------------------------------------------------------------------------- #
#
#   BEFORE:
#       print(f"[{result.status}] {result.name:<28} {result.detail}")
#
#   AFTER:
#       import ui_theme
#       _MAP = {"PASS": "pass", "WARN": "warn", "FAIL": "fail"}
#       ui_theme.print_check(_MAP.get(result.status, "info"),
#                            result.name, result.detail)
#


# --------------------------------------------------------------------------- #
# 3) Where the backend prints 'SERVER IS ONLINE' (e.g. backend/server.py)
# --------------------------------------------------------------------------- #
#
#   BEFORE:
#       print("=====================================================")
#       print("MYPROJECT SERVER IS ONLINE")
#       print("=====================================================")
#       print(f"-> App UI:  {url}")
#       print(f"-> Data Root:     {data_root}")
#       print("=====================================================")
#
#   AFTER:
#       import ui_theme
#       ui_theme.print_server_online(url, data_root, title="MYPROJECT ONLINE")
#


# --------------------------------------------------------------------------- #
# 4) Optional: route your logging through a colored prefix so the
#    [News Aggregator] / [Twitter] lines match the theme.
# --------------------------------------------------------------------------- #
#
#   import logging, ui_theme
#
#   class CyberFormatter(logging.Formatter):
#       LEVELS = {
#           logging.INFO: ("info", "#00e5ff"),
#           logging.WARNING: ("warn", "#ffcc00"),
#           logging.ERROR: ("fail", "#ff2e97"),
#       }
#       def format(self, record):
#           name, color = self.LEVELS.get(record.levelno, ("info", "#9a9a9a"))
#           tag = ui_theme.icon(name) + " " + ui_theme.colorize(
#               record.levelname.lower(), color, bold=True)
#           return f"{tag}  {record.getMessage()}"
#
#   handler = logging.StreamHandler()
#   handler.setFormatter(CyberFormatter())
#   logging.getLogger().addHandler(handler)

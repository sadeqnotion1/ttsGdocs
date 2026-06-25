#!/usr/bin/env bash
# ====================================================================
#  ttsGdocs LAUNCHER (run.sh)
# ====================================================================
#  Runs themed preflight diagnostics (launcher/preflight.py), then starts
#  the local Python TTS backend. The launcher UI has zero required deps and
#  degrades to plain text on terminals without truecolor.
# ====================================================================
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# --- Configuration ---
LAUNCH_CMD="python3 backend/server.py"
# ---------------------

# Themed preflight checks (Python version, TTS engines, port). Never fatal.
if command -v python3 &>/dev/null && [ -f "$DIR/launcher/preflight.py" ]; then
    python3 "$DIR/launcher/preflight.py" || true
fi

echo ""
echo "Launching ttsGdocs backend..."
echo "----------------------------------------------------"
eval "$LAUNCH_CMD" "$@"

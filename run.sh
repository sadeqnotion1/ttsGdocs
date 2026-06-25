#!/usr/bin/env bash
# Launch the TTS backend - keeps the repo root clean.
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/backend/server.py" "$@"

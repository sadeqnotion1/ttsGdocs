# NEXT — the handoff card
_This is the FIRST thing to act on in a new chat (after the START prompt).
The AI rewrites this at the end of every session._

> Repo: https://github.com/sadeqnotion1/ttsGdocs

## ➡️ The one next task
**M1 — Verify real TTS end-to-end.** Install a TTS engine, run the backend, load the
extension in Chrome/Edge, open a real Google Doc, and confirm **Capture & Generate**
produces audio that plays and downloads. Fix any wiring gaps found (CORS, export
fetch, blob handling) with minimal edits.

## Start the next chat with this
> "Let's do M1: verify the Docs-to-Speech flow end-to-end and fix anything that breaks."

## What to paste / give me at the start
Pull these from the repo (or paste them):
1. `backend/server.py` — the endpoint + CORS + audio response.
2. `backend/tts_engine.py` — engine selection + synthesis.
3. `frontend/popup.js` — reads the doc export and calls `/tts`.
4. `frontend/manifest.json` — permissions / host_permissions.
5. Any browser console / server log output from a real run.

## Decisions I need from you for this task
- Which engine to install first for the test: `pyttsx3` (offline) or `gTTS` (online)?
- Confirm the test document (any Google Doc you can open) and expected language.

## Definition of done for this task
- Backend prints `TTS backend on http://127.0.0.1:5000` and `/health` lists ≥1 engine.
- Extension loads with no errors at `chrome://extensions`.
- On a real Google Doc, audio is generated, **plays** in the popup, and **downloads**.
- A file is written under `backend/output/`.
- STATE.md + ROADMAP updated to mark M1 ✅ and point NEXT at M2.

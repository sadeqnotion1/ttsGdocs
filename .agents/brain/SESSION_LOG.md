# SESSION LOG — append-only history
> Repo: https://github.com/sadeqnotion1/ttsGdocs
>
> One short entry per session. Append at the **bottom**. Each entry: date, what we
> did, the verified result, and the exact stop point so the next chat resumes cleanly.

---

## 2026-06-25 — Session 1: scaffold + brain bootstrap
- Scaffolded the Docs-to-Speech starter: Python stdlib TTS server (`backend/`) and
  Chrome/Edge MV3 extension (`frontend/`), thin `run.sh` / `run.bat`, README, .gitignore.
- Installed the `.agents/` brain and built the initial knowledge graph from the real code.
- **Verified:** Python compiles; `manifest.json` valid; both JS files pass `node --check`;
  server boots and prints the bind line; `/health` returns JSON; `/tts` returns a friendly
  503 with no engine and 400 on empty text.
- **Not verified:** real voice synthesis end-to-end (no network/audio engine in the build
  sandbox) and loading the extension in a live browser.
- **Stop point / next:** M1 — verify the full Docs-to-Speech flow end-to-end on the
  maintainer's machine and fix any wiring gaps.


### 2026-06-25 - Added .agents brain + themed launcher
- Installed the `.agents/` brain (STATE, NEXT, ROADMAP, PLAYBOOK, DECISIONS,
  SESSION_LOG, knowledge graph).
- Added the `launcher/` subsystem and wired run.bat / run.sh to it via preflight.py.
- Verified: all Python compiles, the graph renders, the preflight runs.
- Still open: M1 - verify TTS end-to-end (needs a real engine + a logged-in Google Doc).


### 2026-06-25 - Download control (Save As + filename)
- Added `downloads` permission; replaced the anchor with `chrome.downloads`.
- New file-name field in the popup; default derived from the doc title.
- Audio handed to the download as a data URL so it survives popup close.
- Verified: popup.js / content.js pass `node --check`; manifest valid JSON.


### 2026-06-25 - Clearer doc-read errors
- "Could not read the document text" now reports the real cause: empty doc,
  not signed in / not shared, HTTP error, or network/permission.
- Detects Google's HTML sign-in page (status 200) so we never "speak" HTML.
- Added `https://*.googleusercontent.com/*` host permission for export redirects.
- Reminder: Google has no pre-made audio; we synthesize from the doc text.


### 2026-06-25 - Tab-capture recording mode
- Clarified: Google Docs has no downloadable audio; its read-aloud is a live
  voice with no file/API. Our gTTS/pyttsx3 voices are NOT the studio voices.
- Added recording mode (background SW + offscreen + chrome.tabCapture) to
  capture the read-aloud audio to a .webm and Save As.
- New files: frontend/background.js, offscreen.html, offscreen.js; manifest
  gains tabCapture + offscreen + background SW; popup gains a record section.
- Verified: all JS passes node --check; manifest + graph are valid JSON.

# STATE — where we are right now

> Single source of truth. If this disagrees with the real code, the **code wins** —
> tell me and I fix the brain. Repo: https://github.com/sadeqnotion1/ttsGdocs

**Status (one-liner):** M0 scaffold complete — server boots, `/health` and defensive `/tts` verified; real voice synthesis not yet confirmed end-to-end. Next up: M1.

| Part | Status | Notes |
|---|---|---|
| Scaffold & wiring | ✅ | Python stdlib server + MV3 extension. Boots; `/health` returns JSON. |
| Backend `/tts` endpoint | ✅ | Pluggable engines; import-guarded; 503 friendly when no engine, 400 on empty. |
| Extension (read doc + call backend) | 🟦 | Code complete (export-txt read + popup UI). Not yet load-tested in a browser. |
| Real TTS audio end-to-end | ⬜ | ← NEXT (M1). Needs pyttsx3 or gTTS installed + a real doc. |
| Knowledge graph (`.agents/graph/`) | ✅ | Initial graph from real code; regenerate via `render_graph.py`. |
| Brain (`.agents/brain/`) | ✅ | This system. |
| Long-document chunking | ⬜ | M2. |
| Voice / format options | ⬜ | M3. |

> Legend: ✅ done · 🟦 in progress · ⬜ not started · ⚠️ blocked. Mark the active
> task with **← NEXT**.

## Open decisions / questions waiting on you
- Default engine preference for shipping: offline (`pyttsx3`) vs online (`gTTS`)? Currently auto: offline first.
- Target browsers: Chrome/Edge confirmed; do we want a Firefox-ready manifest (M4)?

## Known risks / watch-items
- `pyttsx3` quality/voices depend on the OS speech engine (Linux also needs espeak/espeak-ng).
- Very large docs are sent as a single request — chunking is M2.
- Google Docs export endpoint relies on the user's logged-in session cookies.


> Last touched 2026-06-25: added the `.agents/` brain + `launcher/` subsystem. M1 (verify TTS end-to-end) is still the next task.


> Last touched 2026-06-25: added a tab-capture recording mode (records Google's own read-aloud voices to .webm). Text path (gTTS/pyttsx3) unchanged. Still unverified end-to-end in a real browser.

# ROADMAP — ordered build plan
Build in order. Each milestone is small enough to finish in roughly one chat.
Don't start the next one until the current one's acceptance criteria pass.

> Repo: https://github.com/sadeqnotion1/ttsGdocs

---

- **M0 — Scaffold & wiring** ✅ — Python stdlib server boots; `/health` works; MV3 extension structure in place; `/tts` degrades gracefully when no engine is installed.
- **M1 — Verify real TTS end-to-end** ⬜ **← NEXT** — install an engine, load the extension, generate playable + downloadable audio from a real Google Doc.
- **M2 — Long-document chunking** ⬜ — split large docs into chunks, synthesize per-chunk, concatenate into one audio file; progress feedback.
- **M3 — Voice & format options** ⬜ — voice picker (pyttsx3 voices / gTTS langs), force-MP3 option, surface the saved file path.
- **M4 — Polish** ⬜ — progress bar, richer error states, `prefers-reduced-motion` already done, Firefox-ready manifest, basic settings.

> Mark the active milestone with **← NEXT**. Keep finished ones ✅ with a one-liner.

## Backlog / maybe-later
- Read-aloud highlighting synced to playback.
- Batch-convert multiple docs.
- Optional higher-quality engine (e.g. edge-tts) behind the pluggable interface.

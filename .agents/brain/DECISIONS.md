# DECISIONS — the "why"
> Repo: https://github.com/sadeqnotion1/ttsGdocs
>
> **Append-only.** Never rewrite history; add a new entry. Each decision gets an
> id (D1, D2, ...), a date, the decision, and the reason. Record a decision the
> moment it's made so we don't re-litigate it later.

---

## D1 — 2026-06-25 — Adopt the `.agents/` brain
**Decision:** Use this `.agents/` brain as the single source of truth for AI sessions.
**Why:** Zero-context-loss handoffs between chats/models; no re-explaining state.

## D2 — 2026-06-25 — Read doc text via the plain-text export endpoint
**Decision:** Read a Google Doc by fetching `/document/d/<id>/export?format=txt` with the user's session cookies, instead of scraping the page DOM.
**Why:** Modern Google Docs renders text to a canvas, so DOM scraping is unreliable. The export endpoint returns clean plain text and works with the logged-in session. A text selection is kept as a defensive fallback.

## D3 — 2026-06-25 — Pluggable, import-guarded TTS engines
**Decision:** Support `pyttsx3` (offline, default) and `gTTS` (online) behind one `synthesize()` interface, each import guarded; try in priority order.
**Why:** Lets the user pick offline vs online without code changes, and a missing dependency never crashes the server — it degrades to a friendly 503 with install instructions.

## D4 — 2026-06-25 — Backend on the Python standard library
**Decision:** Implement the server with `http.server` (no Flask/FastAPI).
**Why:** Zero web-framework dependencies; the only real deps are the TTS engines themselves. Keeps the starter trivially runnable.


## D5 - Adopt the CreateProject themed launcher (2026-06-25)
Added `launcher/` (ui_theme.py + demo.py + integration_example.py +
requirements-optional.txt) plus a project-specific `launcher/preflight.py`, and
`init_agents.py` at the repo root. `run.bat` / `run.sh` now run the themed
preflight (banner + Python/engine/port checks), then start `backend/server.py`.
ui_theme has zero required dependencies and degrades to plain text.
Rationale: parity with the CreateProject template; a nicer, self-diagnosing start.


## D6 - Controlled downloads via chrome.downloads (2026-06-25)
The popup no longer uses a plain `<a download>` link. It now adds the
`downloads` permission, an editable file-name field, and calls
`chrome.downloads.download({ saveAs: true, conflictAction: "uniquify" })` so the
user chooses the folder and confirms the name. The audio is passed as a data URL
(not a blob object-URL) so the save still completes if the popup loses focus.
Rationale: real download control (location + name) was the user's explicit ask;
data URL avoids the MV3 popup-closes-and-revokes-blob failure without needing a
background service worker yet.

# ttsGdocs - Docs to Speech (TTS capture)

Capture the text of the **current Google Doc** and turn it into **downloadable speech**.
A tiny Chrome/Edge extension reads the doc; a local Python server does the
text-to-speech.

```
repo-root/
|- backend/            # local Python TTS server (stdlib HTTP, no framework)
|  |- server.py        # entry point: HTTP server + endpoints
|  |- tts_engine.py    # pluggable engines: pyttsx3 (offline) / gTTS (online)
|  |- config.py        # host/port, paths, engine order, defaults
|  |- requirements.txt # install at least one TTS engine
|  `- output/          # generated audio lands here (git-ignored)
|- frontend/           # the Chrome/Edge extension (Manifest V3)
|  |- manifest.json
|  |- content.js       # reads doc id / selection from the page
|  |- popup.html/.css/.js
|  `- icons/
|- .agents/            # AI project brain: orientation, roadmap, decisions, knowledge graph
|- launcher/           # optional themed terminal UI (banner + diagnostics, zero deps)
|- init_agents.py      # installer: sync .agents/ + launcher/ into another repo
|- run.bat             # Windows launcher: themed preflight, then starts the backend
|- run.sh              # macOS/Linux launcher: themed preflight, then starts the backend
|- README.md
`- .gitignore
```

## How it works

1. The extension detects the open doc's id and fetches its **plain-text export**
   (`/document/d/<id>/export?format=txt`) using your existing Google session.
   This is far more reliable than scraping the canvas-rendered page.
2. It POSTs the text to the local server at `http://127.0.0.1:5000/tts`.
3. The server synthesizes audio with the first available engine and returns it.
4. The popup plays it, then lets you **name the file** and pick where to save it via a **Save As** dialog (uses the `chrome.downloads` API).

No invented features: every button maps to a real endpoint, and if no TTS
engine is installed the UI tells you instead of faking output.

## 1. Run the backend

Install at least one engine:

```bash
pip install -r backend/requirements.txt   # both engines, or pick one
# offline only:  pip install pyttsx3   (Linux also needs: espeak / espeak-ng)
# online only:   pip install gTTS
```

Start the server:

```bash
# macOS / Linux
chmod +x run.sh
./run.sh

# Windows
run.bat
```

You should see `TTS backend on http://127.0.0.1:5000`. Open that URL to confirm.

`run.sh` / `run.bat` first run a themed preflight (`launcher/preflight.py`) that
checks your Python version, which TTS engines are installed, and whether the port
is free, then launch the backend. The launcher UI (`launcher/ui_theme.py`) has no
required dependencies; install `pyfiglet` (`pip install -r launcher/requirements-optional.txt`)
only if you want the large ASCII-art banner.

## 2. Load the extension

1. Go to `chrome://extensions` (or `edge://extensions`).
2. Enable **Developer mode**.
3. Click **Load unpacked** and select the `frontend/` folder.
4. Open any Google Doc, click the extension icon, then **Capture & Generate**.

> Firefox: Manifest V3 loads via `about:debugging` > **Load Temporary Add-on**;
> minor manifest tweaks may be needed. Chrome/Edge are the primary targets.

## Endpoints

| Method | Path      | Purpose                                   |
| ------ | --------- | ----------------------------------------- |
| GET    | `/health` | JSON status + which engines are available |
| GET    | `/`       | Human-readable status page                |
| POST   | `/tts`    | Body `{text, rate?, lang?, engine?}` -> audio |

## Configuration

Edit `backend/config.py` to change the host/port, engine priority, default
speed (`DEFAULT_RATE`) or language (`DEFAULT_LANG`).

## AI project brain (`.agents/`)

This repo ships an `.agents/` brain so any AI session (or a new chat/model) can
pick up the project with zero context loss:

- `.agents/AGENTS.md` — read first: orientation + boot sequence.
- `.agents/brain/` — `STATE.md`, `NEXT.md`, `ROADMAP.md`, `PLAYBOOK.md`,
  `DECISIONS.md`, `SESSION_LOG.md` (where we are, what is next, and why).
- `.agents/graph/` — a queryable knowledge graph of the code
  (`graph.json` + `render_graph.py` -> offline `graph.html`).
- `.agents/prompts/` — paste `start.md` to begin a session, `wrap-up.md` to close one.

Regenerate the visual graph after structural changes:

```bash
python .agents/graph/render_graph.py
```

## Notes & limits

- The server binds to `127.0.0.1` only (local machine), not the network.
- Very large documents are sent as one request; chunking is a natural next step.
- `pyttsx3` quality/voices depend on your OS speech engine; `gTTS` needs internet.

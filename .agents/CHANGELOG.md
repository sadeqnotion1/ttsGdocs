# Brain Changelog

Track changes to the **brain itself** here (not project features — those go in the
project's own changelog). Newest on top.

## v2.1 — 2026-06-25 (starter template instantiated for ttsGdocs)
- Instantiated the `.agents/` starter pack for **ttsGdocs**.
- Filled in AGENTS.md project block, STATE.md, NEXT.md, ROADMAP.md, DECISIONS.md, SESSION_LOG.md.
- Built the initial knowledge graph (`graph/graph.json`) from the real backend + frontend code.
- (Template baseline below — keep for reference, prune once the project matures.)

## v2.1 — template baseline
- `prompts/start.md` (#START) and `prompts/wrap-up.md` (#WRAP_UP).
- `brain/SESSION_LOG.md` (append-only session history with stop points).
- `graph/render_graph.py` + generated `graph/graph.html` (offline viewer).
- PLAYBOOK has an explicit Wrap-up checklist (STATE/NEXT/SESSION_LOG/DECISIONS/ROADMAP/graph).
- AGENTS.md boot sequence includes DECISIONS.md and points to the prompts.
- `skills/index.md` registry + `_template/SKILL.md` authoring template.

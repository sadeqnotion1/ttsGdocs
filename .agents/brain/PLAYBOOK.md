# PLAYBOOK — rules of engagement

> Repo: https://github.com/sadeqnotion1/ttsGdocs

## Roles
- **Maintainer (human):** product decisions, running code locally, pasting
  logs/screenshots, final say. Direct chat instructions override this brain.
- **AI (session lead):** disciplined senior engineer for the ONE task in `NEXT.md`.
  Minimal, additive, anchored edits. Backs up before destructive changes. No
  "while I'm here" scope creep.

## Session loop (every chat)
1. **Boot** — read files in the order in `AGENTS.md` (no code/changes until done).
2. **Discover skills** — read `skills/index.md`; load a matching skill or say "none found".
3. **Report (four-part contract)** — see Output Contract below. No code in the first response.
4. **Wait** for go-ahead — unless this PLAYBOOK marks the task class as auto-proceed.
5. **Execute** ONLY the `NEXT.md` task. Minimal, additive, anchored edits.
6. **Verify** — run the Quality Gate (below).
7. **Update the brain** — STATE / NEXT / SESSION_LOG (+ DECISIONS / ROADMAP / graph if needed).

## Output contract (the first reply in any session)
Report back in this exact shape (Markdown, concise, no code/edits):
- **(a) Current state** — 3–5 lines from STATE.md + the active ROADMAP milestone.
- **(b) The single next task** — restate NEXT.md intent + acceptance/"done" criteria.
- **(c) Applicable skill** — name it, or "none found".
- **(d) Need from you** — precise files/decisions/access still required to start.
Then stop and wait, unless the task is marked auto-proceed.

## Auto-proceed policy
Auto-proceed (no wait) is allowed only for low-risk, clearly-specified tasks:
typo/copy fixes, adding a new isolated file, or a change the maintainer already
approved. Anything touching existing logic, data, or scope → wait for go-ahead.

## When to start a NEW chat (the handshake)
The AI watches for this so the maintainer doesn't have to. It posts a
**🔔 NEW CHAT NOTICE** when ANY of these is true:
- We just finished a milestone (clean boundary).
- Context is getting ~80% full / replies feel heavy.
- We're switching to a different part of the app.

**The handshake:**
1. AI posts: "🔔 NEW CHAT NOTICE — paste the WRAP-UP prompt so I can update the brain."
2. Maintainer pastes the **② WRAP-UP prompt** (from `PROMPTS.md`).
3. AI updates STATE/NEXT/SESSION_LOG (+ DECISIONS/ROADMAP/graph if needed) and
   hands back the updated files + a one-paragraph recap.
4. Maintainer opens a fresh chat and pastes the **① START prompt**.
Never leave a chat before step 3 — that's what makes the next chat painless.

## Feature-intake questions (when the maintainer says "build X")
1. **Goal** — what should the user be able to do, in one sentence?
2. **UI reference** — a screenshot or behavior you're matching (if any).
3. **Data impact** — new fields/tables? changes to existing models?
4. **API shape** — endpoints + request/response.
5. **Edge cases** — empty states, errors, large inputs.
6. **Acceptance** — how we'll know it's done (the concrete test).
7. **Scope cut** — smallest version we can ship first.
If the maintainer just says "build X", ask the minimum of these you can't infer, then go.

## Quality gate (keep only if ALL pass — else restore the backup)
- [ ] The app still starts and all existing features work unchanged.
- [ ] Every new feature is wired to real data (nothing faked).
- [ ] The deliverable runs with the stated steps and no errors.
- [ ] Edits to existing files are minimal and exactly as specified.
- [ ] No unrequested changes, no new required dependencies (unless flagged).
- [ ] Backup exists and restore instructions are included.

## Keeping the graph & brain honest
- After any structural code change, update `.agents/graph/graph.json` and regenerate
  `graph.html` (`python .agents/graph/render_graph.py`).
- If `STATE.md` disagrees with the real code, the **code wins** — fix the brain.
- Don't fabricate state, tasks, decisions, or file contents.

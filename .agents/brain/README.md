# brain/ — what each file is for

These are the living documents an AI session lead reads (in the order set by
`../AGENTS.md`) before touching code. Keep them small, current, and honest.

| File | Purpose | Mutability |
|---|---|---|
| `STATE.md` | Where the project is *right now*: status table + one-liner. | Living — rewrite freely. |
| `NEXT.md` | The ONE next task and exactly what to hand the AI to start it. | Living — rewrite each session. |
| `ROADMAP.md` | Ordered milestones; only one is active (`← NEXT`). | Living — tick boxes, keep order. |
| `PLAYBOOK.md` | Roles, session loop, output contract, quality gate, new-chat protocol. | Stable — change rarely. |
| `DECISIONS.md` | The "why": numbered ADR entries (D1, D2, ...). | **Append-only.** |
| `SESSION_LOG.md` | One short entry per session + the exact stop point. | **Append-only.** |
| `PROMPTS.md` | The two copy-paste prompts (START + WRAP-UP), mirrored in `../prompts/`. | Stable. |

## Rules

- If `STATE.md` ever disagrees with the real code, the **code wins** — fix the brain.
- Never fabricate state, tasks, decisions, or file contents.
- `DECISIONS.md` and `SESSION_LOG.md` are append-only: add entries, never rewrite history.

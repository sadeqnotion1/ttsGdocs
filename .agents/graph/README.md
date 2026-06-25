# graph/ — the repo knowledge graph

`graph.json` is a small, hand-maintained map of the codebase: which files/modules
exist, the key functions, and how they relate (calls, imports, http, messaging).
Use it to answer "what calls what" / "where does X live" **without** reading the
whole repo. **Query it; never dump it whole.**

## Schema

```json
{
  "meta":  { "project": "...", "version": 1, "generated": "<ISO-8601>", "note": "..." },
  "nodes": [ { "id": "backend/server.py", "label": "server.py", "group": "backend", "kind": "file", "summary": "..." } ],
  "edges": [ { "source": "frontend/popup.js", "target": "backend/server.py", "kind": "http" } ]
}
```

- **node.id** — stable unique id (use the repo-relative path, optionally `#function`).
- **node.group** — `backend` | `frontend` | `data` | other (drives color in the viewer).
- **node.kind** — `file` | `function` | `module` | `endpoint` | `external`.
- **edge.kind** — `calls` | `imports` | `http` | `messaging` | `reads` | `launches`.

## Query without dumping (jq recipes)

```bash
# List nodes in a group
jq '.nodes[] | select(.group=="backend") | .id' .agents/graph/graph.json

# What does popup.js point to (outgoing edges)?
jq '.edges[] | select(.source=="frontend/popup.js")' .agents/graph/graph.json

# Who points at the backend server (incoming edges)?
jq '.edges[] | select(.target=="backend/server.py")' .agents/graph/graph.json

# Just the counts
jq '{nodes: (.nodes|length), edges: (.edges|length)}' .agents/graph/graph.json
```

## Regenerate the visual

```bash
python .agents/graph/render_graph.py
# -> writes .agents/graph/graph.html (self-contained, offline; open in any browser)
```

Keep the graph honest: after any structural code change, update `graph.json` and
re-run `render_graph.py`.

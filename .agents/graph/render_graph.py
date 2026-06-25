#!/usr/bin/env python3
"""Render .agents/graph/graph.json into a self-contained, offline graph.html.

No external dependencies, no CDN, no network: the data is embedded inline and the
layout is a tiny vanilla-JS force simulation drawn on a <canvas>. Open the result
in any browser. Drag nodes; scroll/hover to read labels.

Usage:
    python .agents/graph/render_graph.py [path/to/graph.json] [-o output.html]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ — knowledge graph</title>
<style>
  :root { color-scheme: dark; }
  html,body { margin:0; height:100%; background:#0A0A14; color:#E5E7EB;
    font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
  #hud { position:fixed; top:12px; left:12px; z-index:10; font-size:13px;
    background:rgba(20,20,32,.7); border:1px solid #2A2A3C; border-radius:10px;
    padding:10px 12px; backdrop-filter: blur(6px); }
  #hud b { color:#8B5CF6; }
  #empty { position:fixed; inset:0; display:flex; align-items:center;
    justify-content:center; color:#9CA3AF; font-size:15px; text-align:center; padding:24px; }
  canvas { display:block; width:100vw; height:100vh; cursor:grab; }
</style>
</head>
<body>
<div id="hud"><b>__TITLE__</b> &middot; <span id="counts"></span></div>
<canvas id="c"></canvas>
<div id="empty" hidden>Graph is empty. Add nodes/edges to graph.json, then re-run render_graph.py.</div>
<script>
const DATA = __DATA__;
const GROUP_COLORS = {backend:'#06B6D4', frontend:'#8B5CF6', data:'#22C55E', default:'#F59E0B'};
const canvas = document.getElementById('c'), ctx = canvas.getContext('2d');
const counts = document.getElementById('counts');
let W, H, DPR;
function resize(){ DPR = window.devicePixelRatio||1; W = canvas.clientWidth; H = canvas.clientHeight;
  canvas.width = W*DPR; canvas.height = H*DPR; ctx.setTransform(DPR,0,0,DPR,0,0); }
window.addEventListener('resize', resize); resize();

const nodes = (DATA.nodes||[]).map((n,i)=>({...n, x: W/2 + Math.cos(i)*120 + (Math.random()-.5)*40,
  y: H/2 + Math.sin(i)*120 + (Math.random()-.5)*40, vx:0, vy:0}));
const byId = Object.fromEntries(nodes.map(n=>[n.id,n]));
const edges = (DATA.edges||[]).filter(e=>byId[e.source]&&byId[e.target])
  .map(e=>({s: byId[e.source], t: byId[e.target], kind: e.kind||''}));
counts.textContent = nodes.length + ' nodes · ' + edges.length + ' edges';
if(!nodes.length){ document.getElementById('empty').hidden = false; }

function color(n){ return GROUP_COLORS[n.group] || GROUP_COLORS.default; }
let dragging=null, mx=0, my=0;
canvas.addEventListener('mousedown',e=>{ const n=pick(e); if(n){dragging=n; canvas.style.cursor='grabbing';} });
window.addEventListener('mousemove',e=>{ const r=canvas.getBoundingClientRect(); mx=e.clientX-r.left; my=e.clientY-r.top;
  if(dragging){ dragging.x=mx; dragging.y=my; dragging.vx=0; dragging.vy=0; } });
window.addEventListener('mouseup',()=>{ dragging=null; canvas.style.cursor='grab'; });
function pick(e){ const r=canvas.getBoundingClientRect(), px=e.clientX-r.left, py=e.clientY-r.top;
  return nodes.find(n=>(n.x-px)**2+(n.y-py)**2 < 144); }

function step(){
  for(let i=0;i<nodes.length;i++) for(let j=i+1;j<nodes.length;j++){
    const a=nodes[i], b=nodes[j]; let dx=a.x-b.x, dy=a.y-b.y; let d2=dx*dx+dy*dy||0.01;
    const f=2200/d2; const d=Math.sqrt(d2); dx/=d; dy/=d;
    a.vx+=dx*f; a.vy+=dy*f; b.vx-=dx*f; b.vy-=dy*f;
  }
  for(const e of edges){ let dx=e.t.x-e.s.x, dy=e.t.y-e.s.y; const d=Math.sqrt(dx*dx+dy*dy)||1;
    const f=(d-90)*0.01; dx/=d; dy/=d; e.s.vx+=dx*f; e.s.vy+=dy*f; e.t.vx-=dx*f; e.t.vy-=dy*f; }
  for(const n of nodes){ if(n===dragging) continue; n.vx+=(W/2-n.x)*0.0008; n.vy+=(H/2-n.y)*0.0008;
    n.vx*=0.85; n.vy*=0.85; n.x+=n.vx; n.y+=n.vy; }
}
function draw(){
  ctx.clearRect(0,0,W,H);
  ctx.strokeStyle='rgba(148,163,184,.25)'; ctx.lineWidth=1;
  for(const e of edges){ ctx.beginPath(); ctx.moveTo(e.s.x,e.s.y); ctx.lineTo(e.t.x,e.t.y); ctx.stroke(); }
  ctx.font='11px Inter, sans-serif'; ctx.textAlign='center';
  for(const n of nodes){ ctx.beginPath(); ctx.fillStyle=color(n); ctx.arc(n.x,n.y,6,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='#CBD5E1'; ctx.fillText(n.label||n.id, n.x, n.y-10); }
}
function loop(){ for(let k=0;k<2;k++) step(); draw(); requestAnimationFrame(loop); }
loop();
</script>
</body>
</html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render graph.json -> offline graph.html")
    ap.add_argument("graph", nargs="?", default=os.path.join(HERE, "graph.json"))
    ap.add_argument("-o", "--output", default=os.path.join(HERE, "graph.html"))
    args = ap.parse_args(argv)

    try:
        with open(args.graph, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("error: %s not found" % args.graph, file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print("error: %s is not valid JSON: %s" % (args.graph, e), file=sys.stderr)
        return 1

    title = (data.get("meta", {}) or {}).get("project") or "Project"
    html = (HTML_TEMPLATE
            .replace("__TITLE__", str(title))
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    n = len(data.get("nodes", []) or [])
    e = len(data.get("edges", []) or [])
    print("wrote %s (%d nodes, %d edges)" % (args.output, n, e))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

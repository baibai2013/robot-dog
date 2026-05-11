#!/usr/bin/env python3
"""
Robot Dog Co. — Live Dashboard
Run: python system/dashboard.py
Open: http://localhost:8888
"""

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
STATE_FILE  = ROOT / "system" / "state.yaml"
ROADMAP_FILE = ROOT / "roadmap" / "roadmap.yaml"
LOG_FILE    = ROOT / "reports" / "log.md"

# ── data ─────────────────────────────────────────────────────────────────────

def load_data():
    with open(STATE_FILE)  as f: state   = yaml.safe_load(f)
    with open(ROADMAP_FILE) as f: roadmap = yaml.safe_load(f)

    tasks_state = state.get("tasks", {})
    total = len(tasks_state)
    done  = sum(1 for t in tasks_state.values() if t.get("status") == "done")

    milestones = []
    for mid, m in roadmap["milestones"].items():
        tasks = []
        for t in m.get("tasks", []):
            tid = t["id"]
            s   = tasks_state.get(tid, {})
            tasks.append({
                "id":         tid,
                "name":       t["name"],
                "domain":     t.get("domain", "—"),
                "status":     s.get("status", "pending"),
                "started":    s.get("started_at", ""),
                "completed":  s.get("completed_at", ""),
                "gate":       t.get("gate", False),
                "notes":      s.get("notes", ""),
            })
        m_done = sum(1 for t in tasks if t["status"] == "done")
        milestones.append({
            "id": mid, "name": m["name"],
            "done": m_done, "total": len(tasks),
            "tasks": tasks,
        })

    blocked = [t for m in milestones for t in m["tasks"] if t["status"] == "blocked_human"]
    active  = [t for m in milestones for t in m["tasks"] if t["status"] == "in_progress"]

    log_lines = []
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text().splitlines()
        log_lines = [l for l in lines if l.startswith("[")][-20:][::-1]

    return {
        "project":    state.get("project", "robot-dog"),
        "updated":    state.get("last_updated", "—"),
        "total":      total,
        "done":       done,
        "pct":        int(done / total * 100) if total else 0,
        "milestones": milestones,
        "blocked":    blocked,
        "active":     active,
        "log":        log_lines,
        "now":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

# ── HTML ──────────────────────────────────────────────────────────────────────

STATUS_META = {
    "done":          ("✅", "#22c55e", "完成"),
    "in_progress":   ("⚡", "#3b82f6", "进行中"),
    "blocked_human": ("🔶", "#f59e0b", "等待审批"),
    "approved":      ("✅", "#22c55e", "已审批"),
    "ready":         ("🟢", "#06b6d4", "就绪"),
    "pending":       ("⬜", "#4b5563", "待解锁"),
    "failed":        ("❌", "#ef4444", "失败"),
}

DOMAIN_COLOR = {
    "mechanical":  "#8b5cf6",
    "electronics": "#06b6d4",
    "firmware":    "#f59e0b",
    "simulation":  "#22c55e",
    "integration": "#ec4899",
    "pm":          "#6b7280",
    "human":       "#f97316",
}

def render(d):
    def badge(status):
        icon, color, label = STATUS_META.get(status, ("?", "#6b7280", status))
        pulse = 'class="pulse"' if status == "in_progress" else ""
        return f'<span {pulse} style="background:{color}22;color:{color};border:1px solid {color}44" class="badge">{icon} {label}</span>'

    def domain_tag(domain):
        color = DOMAIN_COLOR.get(domain, "#6b7280")
        return f'<span style="background:{color}22;color:{color}" class="domain-tag">{domain}</span>'

    def progress_bar(done, total, color="#6366f1"):
        pct = int(done / total * 100) if total else 0
        return f'''
        <div class="progress-track">
          <div class="progress-fill" style="width:{pct}%;background:{color}"></div>
        </div>
        <span class="progress-label">{done}/{total}</span>'''

    # blocked section
    blocked_html = ""
    if d["blocked"]:
        items = "".join(f'''
          <div class="blocked-item">
            <span class="blocked-id">{t["id"]}</span>
            <span class="blocked-name">{t["name"]}</span>
            <span class="blocked-hint">→ 在 system/state.yaml 中将此任务设为 <code>approved</code></span>
          </div>''' for t in d["blocked"])
        blocked_html = f'<div class="alert-box"><div class="alert-title">⚠️ 需要你的决策</div>{items}</div>'

    # active section
    active_html = ""
    if d["active"]:
        items = "".join(f'''
          <div class="active-item">
            <span class="active-dot"></span>
            <span>{t["id"]}</span> — <span style="color:#94a3b8">{t["name"]}</span>
            {domain_tag(t["domain"])}
          </div>''' for t in d["active"])
        active_html = f'<div class="active-box"><div class="active-title">⚡ 正在工作</div>{items}</div>'

    # milestones
    milestones_html = ""
    for m in d["milestones"]:
        all_done = m["done"] == m["total"] and m["total"] > 0
        m_color = "#22c55e" if all_done else "#6366f1"
        tasks_html = "".join(f'''
          <tr class="task-row">
            <td class="task-id">{t["id"]}</td>
            <td>{t["name"]}</td>
            <td>{domain_tag(t["domain"])}</td>
            <td>{badge(t["status"])}</td>
            <td class="task-meta">{"🔑" if t["gate"] else ""}</td>
            <td class="task-meta" style="color:#64748b">{(t["completed"] or t["started"] or "")[:16]}</td>
          </tr>''' for t in m["tasks"])
        milestones_html += f'''
        <div class="milestone-card">
          <div class="milestone-header">
            <span class="milestone-id">{m["id"]}</span>
            <span class="milestone-name">{m["name"]}</span>
            <div class="milestone-progress">
              {progress_bar(m["done"], m["total"], m_color)}
            </div>
          </div>
          <table class="task-table">
            <thead><tr>
              <th>ID</th><th>任务</th><th>部门</th><th>状态</th><th></th><th>时间</th>
            </tr></thead>
            <tbody>{tasks_html}</tbody>
          </table>
        </div>'''

    # log
    log_html = "".join(
        f'<div class="log-line">{line}</div>' for line in d["log"]
    ) or '<div class="log-line" style="color:#4b5563">暂无记录</div>'

    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="8">
  <title>Robot Dog Co. — Dashboard</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, "SF Pro Display", "Segoe UI", sans-serif;
      background: #080b14;
      color: #e2e8f0;
      min-height: 100vh;
      padding: 24px;
    }}
    a {{ color: inherit; text-decoration: none; }}
    code {{ font-family: "SF Mono", monospace; font-size: 0.8em;
            background: #1e293b; padding: 1px 6px; border-radius: 4px; }}

    /* header */
    .header {{ display:flex; align-items:center; justify-content:space-between;
               margin-bottom:28px; }}
    .logo {{ font-size:1.5rem; font-weight:700; letter-spacing:-0.5px; }}
    .logo span {{ color:#6366f1; }}
    .header-meta {{ font-size:.8rem; color:#475569; text-align:right; }}
    .live-dot {{ display:inline-block; width:7px; height:7px; border-radius:50%;
                 background:#22c55e; margin-right:5px; animation:blink 2s infinite; }}
    @keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:.3}} }}

    /* overall progress */
    .overall-card {{
      background: linear-gradient(135deg, #1e1b4b 0%, #1a1d2e 100%);
      border: 1px solid #312e81;
      border-radius: 14px; padding: 20px 24px;
      margin-bottom: 20px;
      display: flex; align-items: center; gap: 24px;
    }}
    .overall-label {{ font-size:.85rem; color:#818cf8; font-weight:500; }}
    .overall-pct {{ font-size:2.5rem; font-weight:800; color:#a5b4fc; line-height:1; }}
    .overall-sub {{ font-size:.8rem; color:#6366f1; margin-top:3px; }}
    .overall-bar {{ flex:1; }}
    .overall-track {{ height:10px; background:#1e293b; border-radius:10px; overflow:hidden; }}
    .overall-fill {{ height:100%; border-radius:10px;
                     background: linear-gradient(90deg, #6366f1, #8b5cf6);
                     transition: width .6s ease; }}

    /* alert + active */
    .alert-box {{ background:#1c1407; border:1px solid #92400e44;
                  border-left: 3px solid #f59e0b;
                  border-radius:10px; padding:16px 20px; margin-bottom:16px; }}
    .alert-title {{ color:#f59e0b; font-weight:600; font-size:.85rem;
                    margin-bottom:10px; }}
    .blocked-item {{ display:flex; align-items:center; gap:10px;
                     padding:6px 0; border-top:1px solid #92400e22; font-size:.85rem; }}
    .blocked-id {{ color:#fbbf24; font-family:monospace; font-size:.8rem;
                   background:#2d1f00; padding:2px 8px; border-radius:4px; min-width:180px; }}
    .blocked-name {{ flex:1; }}
    .blocked-hint {{ color:#6b7280; font-size:.78rem; }}
    .active-box {{ background:#071c1c; border:1px solid #065f4644;
                   border-left: 3px solid #06b6d4;
                   border-radius:10px; padding:16px 20px; margin-bottom:16px; }}
    .active-title {{ color:#06b6d4; font-weight:600; font-size:.85rem; margin-bottom:10px; }}
    .active-item {{ display:flex; align-items:center; gap:10px;
                    font-size:.85rem; padding:4px 0; }}
    .active-dot {{ width:8px; height:8px; border-radius:50%; background:#3b82f6;
                   animation: pulse-dot 1.5s infinite; flex-shrink:0; }}
    @keyframes pulse-dot {{ 0%,100%{{transform:scale(1);opacity:1}} 50%{{transform:scale(1.4);opacity:.6}} }}

    /* badges */
    .badge {{ font-size:.75rem; padding:3px 9px; border-radius:20px;
              font-weight:500; white-space:nowrap; }}
    .pulse {{ animation: pulse-badge 1.5s infinite; }}
    @keyframes pulse-badge {{ 0%,100%{{opacity:1}} 50%{{opacity:.6}} }}
    .domain-tag {{ font-size:.72rem; padding:2px 8px; border-radius:4px;
                   font-weight:500; white-space:nowrap; }}

    /* milestone cards */
    .milestone-card {{
      background: #0f1626; border: 1px solid #1e293b;
      border-radius: 12px; margin-bottom: 16px; overflow: hidden;
    }}
    .milestone-header {{
      display: flex; align-items: center; gap: 14px;
      padding: 14px 20px; background: #111827;
      border-bottom: 1px solid #1e293b;
    }}
    .milestone-id {{ font-size:.75rem; font-weight:700; color:#6366f1;
                     background:#1e1b4b; padding:3px 10px; border-radius:6px; }}
    .milestone-name {{ font-weight:600; font-size:.95rem; flex:1; }}
    .milestone-progress {{ display:flex; align-items:center; gap:10px; }}
    .progress-track {{ width:100px; height:6px; background:#1e293b;
                       border-radius:6px; overflow:hidden; }}
    .progress-fill {{ height:100%; border-radius:6px; transition:width .5s ease; }}
    .progress-label {{ font-size:.78rem; color:#64748b; white-space:nowrap; }}

    /* task table */
    .task-table {{ width:100%; border-collapse:collapse; font-size:.83rem; }}
    .task-table th {{ padding:8px 16px; text-align:left; color:#475569;
                      font-weight:500; font-size:.75rem; text-transform:uppercase;
                      letter-spacing:.05em; border-bottom:1px solid #1e293b; }}
    .task-row {{ border-bottom:1px solid #0f172a; }}
    .task-row:last-child {{ border-bottom:none; }}
    .task-row:hover {{ background:#111827; }}
    .task-table td {{ padding:10px 16px; vertical-align:middle; }}
    .task-id {{ font-family:monospace; font-size:.78rem; color:#6366f1; }}
    .task-meta {{ color:#475569; font-size:.78rem; white-space:nowrap; }}

    /* log */
    .log-card {{ background:#0f1626; border:1px solid #1e293b;
                 border-radius:12px; padding:16px 20px; margin-top:20px; }}
    .log-title {{ font-size:.85rem; font-weight:600; color:#475569;
                  margin-bottom:12px; text-transform:uppercase; letter-spacing:.08em; }}
    .log-line {{ font-family:monospace; font-size:.78rem; color:#64748b;
                 padding:4px 0; border-bottom:1px solid #0f172a; }}
    .log-line:first-child {{ color:#94a3b8; }}

    /* grid */
    .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px; }}
    @media(max-width:800px) {{ .two-col {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>

<div class="header">
  <div class="logo">🤖 Robot Dog <span>Co.</span></div>
  <div class="header-meta">
    <div><span class="live-dot"></span>自动刷新 · 每 8 秒</div>
    <div>最后更新: {d["now"]}</div>
  </div>
</div>

<div class="overall-card">
  <div>
    <div class="overall-label">总体进度</div>
    <div class="overall-pct">{d["pct"]}%</div>
    <div class="overall-sub">{d["done"]} / {d["total"]} 任务完成</div>
  </div>
  <div class="overall-bar">
    <div class="overall-track">
      <div class="overall-fill" style="width:{d["pct"]}%"></div>
    </div>
  </div>
  <div style="text-align:right;font-size:.8rem;color:#475569">
    <div>项目: <span style="color:#a5b4fc">{d["project"]}</span></div>
    <div>状态更新: {d["updated"]}</div>
  </div>
</div>

{blocked_html}
{active_html}

<div style="font-size:.75rem;color:#475569;margin-bottom:12px;font-weight:600;
            text-transform:uppercase;letter-spacing:.08em;">
  里程碑与任务
</div>

{"".join(f'<div class="milestone-card">' + m + '</div>' if False else m for m in [milestones_html])}

<div class="log-card">
  <div class="log-title">📋 活动日志</div>
  {log_html}
</div>

<div style="text-align:center;margin-top:24px;font-size:.75rem;color:#1e293b">
  robot-dog · local dashboard · python system/dashboard.py
</div>

</body></html>"""

# ── server ────────────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass  # suppress request logs

    def do_GET(self):
        if self.path == "/api/state":
            data = load_data()
            body = json.dumps(data, ensure_ascii=False, default=str).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        else:
            try:
                data = load_data()
                html = render(data).encode()
            except Exception as e:
                html = f"<pre style='color:red'>Error: {e}</pre>".encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(html))
            self.end_headers()
            self.wfile.write(html)


if __name__ == "__main__":
    port = 8888
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"✅ Dashboard running → http://localhost:{port}")
    print(f"   API endpoint   → http://localhost:{port}/api/state")
    print("   Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

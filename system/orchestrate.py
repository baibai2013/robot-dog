#!/usr/bin/env python3
"""
Robot Dog Project Orchestrator
--------------------------------
Usage:
  python system/orchestrate.py          # show status + advance one task
  python system/orchestrate.py --status # show status only, no dispatch
  python system/orchestrate.py --report # generate progress report
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
STATE_FILE = ROOT / "system" / "state.yaml"
ROADMAP_FILE = ROOT / "roadmap" / "roadmap.yaml"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


# ── helpers ──────────────────────────────────────────────────────────────────

def load(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def save_state(state: dict):
    state["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(STATE_FILE, "w") as f:
        yaml.dump(state, f, allow_unicode=True, default_flow_style=False)

def find_task_in_roadmap(task_id: str, roadmap: dict) -> dict | None:
    for milestone in roadmap["milestones"].values():
        for task in milestone.get("tasks", []):
            if task["id"] == task_id:
                return task
    return None

def all_deps_done(task_id: str, state: dict, roadmap: dict) -> bool:
    task = find_task_in_roadmap(task_id, roadmap)
    if not task:
        return False
    for dep in task.get("depends_on", []):
        if state["tasks"].get(dep, {}).get("status") != "done":
            return False
    return True


# ── status display ────────────────────────────────────────────────────────────

STATUS_ICON = {
    "done": "✅",
    "in_progress": "🔄",
    "blocked_human": "🔶",
    "approved": "✅",
    "ready": "🟢",
    "pending": "⬜",
    "failed": "❌",
}

def print_status(state: dict, roadmap: dict):
    print(f"\n{'='*60}")
    print(f"  ROBOT DOG PROJECT — {state.get('last_updated', 'unknown')}")
    print(f"  Current milestone: {state.get('current_milestone', '?')}")
    print(f"{'='*60}\n")

    for mid, milestone in roadmap["milestones"].items():
        m_tasks = milestone.get("tasks", [])
        statuses = [state["tasks"].get(t["id"], {}).get("status", "pending") for t in m_tasks]
        done_count = sum(1 for s in statuses if s == "done")
        print(f"  [{mid}] {milestone['name']}  ({done_count}/{len(m_tasks)})")
        for task in m_tasks:
            tid = task["id"]
            s = state["tasks"].get(tid, {}).get("status", "pending")
            icon = STATUS_ICON.get(s, "?")
            gate = " 🔑[GATE]" if task.get("gate") else ""
            print(f"       {icon} {tid}: {task['name']}{gate}")
        print()


# ── find next task ────────────────────────────────────────────────────────────

def find_next_task(state: dict, roadmap: dict) -> str | None:
    """Return the first task that is 'ready' and has all deps done."""
    tasks = state["tasks"]

    # promote pending → ready if deps satisfied
    for task_id, info in tasks.items():
        if info.get("status") == "pending" and all_deps_done(task_id, state, roadmap):
            info["status"] = "ready"

    # find first ready (not blocked, not human-only)
    for task_id, info in tasks.items():
        if info.get("status") == "ready":
            rd_task = find_task_in_roadmap(task_id, roadmap)
            if rd_task and rd_task.get("owner") != "human":
                return task_id

    return None


# ── dispatch ──────────────────────────────────────────────────────────────────

DOMAIN_PROMPT = {
    "mechanical": "你是机械设计工程师。使用 build123d 进行 CAD 建模，输出尺寸规格和设计文档。",
    "electronics": "你是电子硬件工程师。负责原理图设计、元器件选型、PCB 规划。",
    "firmware": "你是嵌入式固件工程师。负责通信协议定义和电机控制代码。",
    "simulation": "你是运动控制仿真工程师。使用 PyBullet/ROS 进行步态和运动学仿真。",
    "integration": "你是系统集成工程师。负责跨域一致性验证和最终集成检查。",
    "pm": "你是项目经理。负责协调各域输出和交叉验证。",
}

def build_agent_prompt(task: dict, roadmap_task: dict) -> str:
    domain = roadmap_task.get("domain", "pm")
    role = DOMAIN_PROMPT.get(domain, "你是工程师。")
    outputs = roadmap_task.get("outputs", [])
    outputs_str = "\n".join(f"  - {o}" for o in outputs)
    deps = roadmap_task.get("depends_on", [])
    deps_str = ", ".join(deps) if deps else "无"

    return f"""
{role}

## 当前任务
ID: {roadmap_task['id']}
名称: {roadmap_task['name']}
描述: {roadmap_task.get('description', '')}

## 依赖的上游输出
{deps_str}
请先阅读依赖任务的输出文件（在 domains/ 目录下），再开始当前任务。

## 期望输出
{outputs_str}

## 完成要求
1. 将主要产出写入上述 outputs 路径
2. 在 reports/log.md 追加一行摘要：`[{datetime.now().strftime('%Y-%m-%d')}] {roadmap_task['id']}: <一句话完成说明>`
3. 完成后输出 DONE: {roadmap_task['id']}

项目根目录: {ROOT}
""".strip()


def dispatch(task_id: str, state: dict, roadmap: dict):
    roadmap_task = find_task_in_roadmap(task_id, roadmap)
    if not roadmap_task:
        print(f"[ERROR] Task {task_id} not found in roadmap")
        return

    prompt = build_agent_prompt(state["tasks"][task_id], roadmap_task)

    print(f"\n▶ Dispatching: {task_id}")
    print(f"  Domain: {roadmap_task.get('domain')}")
    print(f"  Task: {roadmap_task['name']}\n")

    # mark in_progress
    state["tasks"][task_id]["status"] = "in_progress"
    state["tasks"][task_id]["started_at"] = datetime.now().isoformat()
    save_state(state)

    # call claude CLI
    result = subprocess.run(
        ["claude", "--print", prompt],
        cwd=ROOT,
        capture_output=False,
        text=True,
    )

    if result.returncode == 0:
        state["tasks"][task_id]["status"] = "done"
        state["tasks"][task_id]["completed_at"] = datetime.now().isoformat()
        print(f"\n✅ Done: {task_id}")
    else:
        state["tasks"][task_id]["status"] = "failed"
        print(f"\n❌ Failed: {task_id} (exit {result.returncode})")

    save_state(state)


# ── report ────────────────────────────────────────────────────────────────────

def generate_report(state: dict, roadmap: dict):
    lines = [f"# Progress Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    total = len(state["tasks"])
    done = sum(1 for t in state["tasks"].values() if t.get("status") == "done")
    blocked = sum(1 for t in state["tasks"].values() if t.get("status") == "blocked_human")

    lines.append(f"**Overall: {done}/{total} tasks done, {blocked} awaiting your input**\n")

    for mid, milestone in roadmap["milestones"].items():
        tasks = milestone.get("tasks", [])
        done_c = sum(1 for t in tasks if state["tasks"].get(t["id"], {}).get("status") == "done")
        lines.append(f"## {mid}: {milestone['name']} ({done_c}/{len(tasks)})")
        for task in tasks:
            s = state["tasks"].get(task["id"], {}).get("status", "pending")
            lines.append(f"- [{s}] {task['id']}: {task['name']}")
        lines.append("")

    # pending human gates
    lines.append("## Action Required from You")
    needs_action = False
    for task_id, info in state["tasks"].items():
        if info.get("status") in ("blocked_human",):
            rd = find_task_in_roadmap(task_id, roadmap)
            if rd:
                lines.append(f"- **{task_id}**: {rd['name']}")
                lines.append(f"  > {rd.get('description', '')}")
                needs_action = True
    if not needs_action:
        lines.append("- None at this time")

    report_path = REPORTS_DIR / f"report-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
    report_path.write_text("\n".join(lines))
    print(f"\n📊 Report saved: {report_path}")
    print("\n".join(lines))


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Robot Dog Orchestrator")
    parser.add_argument("--status", action="store_true", help="Show status only")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--run", metavar="TASK_ID", help="Force-run a specific task")
    args = parser.parse_args()

    state = load(STATE_FILE)
    roadmap = load(ROADMAP_FILE)

    print_status(state, roadmap)

    if args.status:
        return

    if args.report:
        generate_report(state, roadmap)
        return

    if args.run:
        dispatch(args.run, state, roadmap)
        return

    next_task = find_next_task(state, roadmap)
    if next_task:
        dispatch(next_task, state, roadmap)
    else:
        print("⏸  No tasks ready to run.")
        print("   Check blocked_human tasks — they need your approval in state.yaml")


if __name__ == "__main__":
    main()

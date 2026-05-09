#!/usr/bin/env python3
"""仅扫描 **OPEN** issues：哪些已有「## 🔍 Issue 解读」、哪些待解读（CLOSED 不参与）。

使用 GitHub GraphQL 分页拉取（states 仅 OPEN）。

在**仓库根目录**执行：
  python3 .skills/github-issues/scripts/scan_issue_interpretation_status.py

输出：
  tmp/issues-need-interpret.json
    — { "done": [编号...], "need": [{number,state,title}, ...] }  # 均为 OPEN
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_PATH = REPO_ROOT / "tmp" / "issues-need-interpret.json"

MARKER = "## 🔍 Issue 解读"

QUERY = """
query($cursor: String) {
  repository(owner: "aotianlong", name: "container-house") {
    issues(first: 100, after: $cursor, states: [OPEN]) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number
        state
        title
        body
        comments(first: 100) {
          nodes { body }
        }
      }
    }
  }
}
"""


def has_interpretation(text: str) -> bool:
    if not text:
        return False
    if MARKER in text:
        return True
    return "Issue 解读" in text and "🔍" in text


def run_graphql(cursor: str | None = None) -> dict:
    args = ["gh", "api", "graphql", "-f", f"query={QUERY}"]
    if cursor:
        args.extend(["-f", f"cursor={cursor}"])
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(r.stderr or r.stdout)
    return json.loads(r.stdout)


def main() -> None:
    cursor = None
    all_nodes: list = []
    while True:
        data = run_graphql(cursor)
        conn = data["data"]["repository"]["issues"]
        all_nodes.extend(conn["nodes"])
        if not conn["pageInfo"]["hasNextPage"]:
            break
        cursor = conn["pageInfo"]["endCursor"]

    done: list[int] = []
    need: list[dict] = []
    for node in all_nodes:
        n = node["number"]
        body = node.get("body") or ""
        if has_interpretation(body):
            done.append(n)
            continue
        ctexts = [c.get("body") or "" for c in node.get("comments", {}).get("nodes", [])]
        if any(has_interpretation(t) for t in ctexts):
            done.append(n)
        else:
            need.append(
                {
                    "number": n,
                    "state": node["state"],
                    "title": node.get("title") or "",
                }
            )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "done": sorted(done),
        "need": sorted(need, key=lambda x: x["number"]),
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OPEN issues: {len(all_nodes)}")
    print(f"已有解读标记（防重复）: {len(done)}")
    print(f"待解读: {len(need)}")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

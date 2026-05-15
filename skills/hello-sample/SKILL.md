---
name: hello-sample
description: >-
  演示 yoo-ai-skills 仓库中的最小 skill：说明本仓库如何统一写入 Cursor / Claude Code / Codex。
  在用户问起「skills 从哪里来」「如何分发」时使用。
---

# Hello Sample（示例 Skill）

## 用途

这是一个占位示例，验证各工具均能识别标准 `SKILL.md`（含 `name` 与 `description` 必填字段）。

## 使用指引

1. 在本仓库的 `skills/<skill-slug>/` 下维护技能内容与可选脚本。
2. 运行 `yoo-ai-skills sync`，将技能同步或链接到各工具默认目录：
   - Cursor：`~/.cursor/skills/<slug>/`
   - Claude Code：`~/.claude/skills/<slug>/`
   - Codex：`~/.codex/skills/<slug>/`
   - Agents（通用）：`~/.agents/skills/<slug>/`
3. 在对应工具中按需显式唤起 skill，或依赖 `description` 中的触发词进行隐式匹配（视工具能力而定）。

## 维护注意

- 保持 `name` 与目录名（slug）一致，便于脚本与人工查找。
- `description` 同时影响各工具的「何时选用」；写清能力边界与触发词。

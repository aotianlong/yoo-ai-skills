# yoo-ai-skills

在单一仓库维护符合 [Agent Skills](https://agentskills.io/) 形态的 `SKILL.md` 技能，并通过 CLI 同步到多套 AI 工具的默认目录。

## 目录结构

```text
yoo-ai-skills/
├── bin/
│   └── yoo-ai-skills.mjs    # CLI 入口（无需构建）
├── config/
│   └── targets.defaults.json # 各工具 skills 根目录映射（可复制为本地覆盖）
├── skills/                   # 统一技能源（每个子文件夹 = 一个 skill）
│   └── <skill-slug>/
│       ├── SKILL.md          # 必填：name / description frontmatter + 正文
│       └── ...               # 可选：脚本、参考资料等
├── package.json
└── README.md
```

`<skill-slug>` 建议与 frontmatter 里的 `name` 保持一致。

## CLI

```bash
# 列出仓库内可识别的 skills（必须有 skills/<slug>/SKILL.md）
npm run list
# 或：node ./bin/yoo-ai-skills.mjs list

# 同步到本机 Cursor / Claude Code / Codex 默认路径（符号链接）
node ./bin/yoo-ai-skills.mjs sync

# 只看计划：node ./bin/yoo-ai-skills.mjs sync --dry-run
# 指定目标：node ./bin/yoo-ai-skills.mjs sync --targets cursor,codex
# 单个技能：node ./bin/yoo-ai-skills.mjs sync --skill hello-sample
# 拷贝模式：node ./bin/yoo-ai-skills.mjs sync --method copy
```

全局安装后可使用：

```bash
npm link   # 在仓库根目录执行一次
yoo-ai-skills list
yoo-ai-skills sync
```

### 默认目标路径

| 工具 | skills 根目录 |
|------|----------------|
| Cursor | `~/.cursor/skills/` |
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |

可在 `config/targets.defaults.json` 查看或按需修改。**优先** symlink，使编辑仓库即生效；仅在不支持符号链接的环境使用 `--method copy`。

## License

MIT

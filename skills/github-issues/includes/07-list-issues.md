[← 技能索引](../SKILL.md)

# 列出 Issues（只读）

当用户想用自然语言**查看、罗列、筛选** GitHub Issues 时进入此流程。属于**只读**，无需「先规划再等确认」（与 [`SKILL.md`](../SKILL.md) 总规则一致）。

## 触发说法（示例）

- 「列出 issues」「列出 open issues」「看看有哪些 issue」
- 「issue 列表」「当前仓库的 issues」「查一下 github 上的 issues」
- 「按标签 xxx 筛 issues」「谁 assign 给我的 issue」
- 「最近关了哪些 issue」「closed 的 issue 有哪些」

## Step L1：确定仓库

1. 若用户在对话里给了 **`owner/repo`** 或 issue/PR 链接，从中解析仓库。
2. 否则若当前 shell 已在某 git 仓库下且该仓库与 GitHub 关联，可用：`gh repo view --json nameWithOwner -q .nameWithOwner`（或在仓库根执行 `gh issue list`，`gh` 会默认当前仓库）。
3. 若仍不明确，且任务上下文来自本技能常用项目，默认 **`aotianlong/container-house`**（见 [`00-common.md`](00-common.md)）。**不要猜**：用户明确指其他仓库时以用户为准。

跨仓库时统一加：`gh issue list -R owner/repo ...`

## Step L2：确认状态与筛选

向用户意图对齐（可从对话直接推断，不必逐条追问）：

| 意图 | `gh issue list` 常用参数 |
|------|-------------------------|
| 默认 / 未完成 | 省略 `--state` 时 **`gh` 默认仅 open**；也可显式写 `--state open` |
| 含已关闭 | `--state all` 或 `--state closed` |
| 按标签 | `-l "bug,enhancement"` 或重复 `-l` |
| 按负责人 | `-a @me` 或 `-a login` |
| 按作者 | `-A login`（`--author`） |
| 关键词 | `--search "文案 关键词"` |
| 只看最近若干条 | `-L 30`（数字可调） |

## Step L3：执行并呈现

**人类可读（终端表格）**；`gh issue ls` 与 `gh issue list` 等价：

```bash
gh issue list -R owner/repo --state open -L 50
```

在浏览器中打开列表：`gh issue list -R owner/repo -w`。

**结构化（便于在对话里汇总、排序、去重）**：

```bash
gh issue list -R owner/repo --state open -L 100 \
  --json number,title,state,labels,assignees,updatedAt,url \
  -q '.[] | "#\(.number) [\(.state)] \(.title) \(.url)"'
```

可按需增删 `--json` 字段（如 `milestone`、`createdAt`）。**字段名以 `gh issue list --help` 中 `--json` 说明为准**。

## 与其它步骤的配合

- 列出后用户若说「解读 #xxx」「解决 #xxx」，分别转入 [`02-issue-interpretation.md`](02-issue-interpretation.md)、[`03-issue-fix.md`](03-issue-fix.md)。
- 需要**单条详情**时用：`gh issue view <number> -R owner/repo`，或加 `--comments` 看评论。

## 注意事项

- 全程**不**创建、编辑、关闭 issue；仅 `list` / `view`。
- 若 `gh` 未登录或无权访问私有仓库，说明错误并提示用户检查 `gh auth status` 与仓库权限。

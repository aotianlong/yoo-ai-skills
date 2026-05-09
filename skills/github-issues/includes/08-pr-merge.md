[← 技能索引](../SKILL.md)

# 合并 GitHub PR（含冲突与关联 Issue）

## 触发条件

当用户说以下任意形式时，进入本流程（**将改远程仓库与 issue 状态**；除非用户已说「直接执行」等，否则应先简要说明计划再动手）：

- 「合并 PR #xxx」「merge PR #xxx」「把 PR #xxx 合进 dev」
- 「帮我合并这个 PR」+ PR 编号或链接
- 「PR 合一下」「关闭 PR 并关 issue」（且语境为**合并**而非仅关闭 PR）

---

## 阶段一：确认目标与仓库

- 从用户话术中取得 **PR 编号**（或 `gh pr view <url>` 解析）。
- 使用 `gh` 时**显式或隐式**指向正确仓库：默认与业务仓库一致时为 `aotianlong/container-house`；若当前目录 git remote 即该仓库，可依赖 `gh` 自动检测，否则加 `--repo OWNER/REPO`。

---

## 阶段二：检查 PR 是否已合并（必做）

### Step M1：拉取 PR 元数据

```bash
gh pr view {PR_NUMBER} --repo aotianlong/container-house \
  --json number,title,state,mergedAt,closedAt,mergeStateStatus,mergeable,baseRefName,headRefName,url,body,closingIssuesReferences
```

### Step M2：判定

| 条件 | 处理 |
|------|------|
| `mergedAt` **非空** | **停止合并**。在对话中说明「该 PR 已合并」并给出 `mergedAt`、PR URL。继续执行下方 **「已合并后的关联 Issue 检查」**（确保相关 issue 已关；见阶段五）。**不要**再次执行 `gh pr merge`。 |
| `state` 为 `CLOSED` 且 `mergedAt` 为空 | PR 已关闭且**未合并**：说明情况，**不要**执行 merge；与用户确认是否改为重开 / 新 PR。 |
| `state` 为 `OPEN` | 进入 **阶段三**。 |

---

## 阶段三：合并阻塞与冲突处理

### Step M3：可读性检查（建议 Human 层快速看 JSON）

- `mergeStateStatus`：`CLEAN` 表示可尝试合并；`DIRTY` 表示**有冲突**；`BLOCKED` 可能为未过审、分支保护、必需检查失败等。
- `reviewDecision`（可选再查）：`gh pr view {N} --json reviewDecision,statusCheckRollup`
- 若为 **Draft**，须先 `gh pr ready {N}` 或请用户标记为可审（依团队规范）。

### Step M4：存在冲突时（`mergeStateStatus` 为 `DIRTY` 或 merge 报错冲突）

在**主仓库根**或独立 worktree 中处理，避免污染无关分支：

1. 检出 PR 头部分支（推荐）：

```bash
cd "$(git rev-parse --show-toplevel)"   # 业务仓库根
git fetch origin
gh pr checkout {PR_NUMBER} --repo aotianlong/container-house
```

2. 将 **base** 合入当前分支（`baseRefName` 来自 Step M1，多为 `dev`）：

```bash
BASE="$(gh pr view {PR_NUMBER} --repo aotianlong/container-house --json baseRefName -q .baseRefName)"
git fetch origin "$BASE"
git merge "origin/$BASE"
```

3. 解决冲突 → `git add` → **合并提交**：

```bash
git commit   # 完成 merge commit；信息可写 fix: resolve merge with origin/<BASE> for PR #N
git push origin HEAD
```

4. 再次执行 Step M1 或 `gh pr view ... mergeStateStatus`，确认变为 `CLEAN`（或 `mergeable: MERGEABLE`）后进入 **阶段四**。

> **注意**：若团队规定用 **rebase** 而非 merge 消冲突，可改为 `git rebase origin/$BASE`，但需 force-with-lease 推送前**征得用户同意**（改写 PR 历史）。

### Step M5：非冲突类阻塞

- **Required review / 检查失败**：先按 `06-pr-review.md` 处理（修代码、push、Approve 或修 CI），再回来合并。
- **Not mergeable（策略原因）**：向用户说明具体检查项，不要强行 `--admin` 除非用户明确要求且你有权限。

---

## 阶段四：执行合并

在确认 **未合并**、**可合并**、**无未解决冲突** 后：

```bash
gh pr merge {PR_NUMBER} --repo aotianlong/container-house --merge
```

- 若仓库惯例为 **squash** 或 **rebase**，改用 `--squash` 或 `--rebase`（与团队一致）；不确定时**先问用户**。
- 需要删除远程分支时可加 `--delete-branch`（按需）。

若命令失败，根据 stderr 提示回到阶段三或 M5。

---

## 阶段五：合并后 — 关联 Issue 与关闭

### 5.1 GitHub 自动关闭

若 PR 正文中已有 `Closes #` / `Fixes #` / `Resolves #` 等关键词，**合并成功后 GitHub 通常会关闭对应 issue**。仍需做 **5.2 校验**，避免遗漏。

### 5.2 校验 `closingIssuesReferences` 与仍 OPEN 的编号

1. 再次查看（合并后 `mergedAt` 应有值）：

```bash
gh pr view {PR_NUMBER} --repo aotianlong/container-house \
  --json mergedAt,closingIssuesReferences
```

2. `closingIssuesReferences` 为对象列表，可取 `number` 字段。对每个编号：

```bash
gh issue view {ISSUE_NUMBER} --repo aotianlong/container-house --json state,title -q .
```

3. 对 **`state` 仍为 `OPEN`** 的 issue（自动关闭未生效或仅「关联」未写关闭关键词时），**手动关闭**并简要说明：

```bash
gh issue close {ISSUE_NUMBER} --repo aotianlong/container-house \
  --reason completed \
  --comment "$(cat <<'EOF'
已在 PR #{PR_NUMBER} 合并中交付，关闭本 issue。

PR: <粘贴 PR url>
EOF
)"
```

4. 若 Step M1 显示 **已合并**而用户仍请求「合并」，对 `closingIssuesReferences` 中仍 OPEN 的 issue 同样执行 **5.2 第 3 步**（仅补关 issue，不重复 merge）。

### 5.3 可选：从 PR body 补充「相关」编号

当正文用了 `Ref #` / `See #` 等**不会**自动关 issue 的引用，而用户明确要求「关闭相关 issue」时：在对话中列出这些编号，**征得用户确认**后再 `gh issue close`，避免误关无关任务。

---

## 输出建议

在对话中汇总：

- PR 是否新合并 / 早已合并
- 是否做过冲突解决（若有，列关键文件）
- 已关闭或确认已关闭的 issue 列表
- 若有 OPEN 的关联项因政策不能关，说明原因

---

## 与其它分片的关系

- 合并前代码质量、Approve：[`06-pr-review.md`](06-pr-review.md)
- 父/子 issue、`Closes #父` 策略：[`07-sub-issues.md`](07-sub-issues.md)

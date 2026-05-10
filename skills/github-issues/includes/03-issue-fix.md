[← 技能索引](../SKILL.md)

# Issue 解决流程

## Issue 解决流程（用户要求逐个解决时）

### 默认：直接全量实现（用户未要求「先解读 / 先规划」时）

当用户说以下任意形式，且**未**在同一任务中要求 **先解读**、**先分析再改**、**只规划不写代码**、**两步走**、**方案定了再改**、**输出规划等我确认** 等时，**应用本技能**并**直接进入**「分支优先」与阶段一～五中的实现（读 issue、必要截图/只读检索后，即可在仓库根主工作树 `checkout` 修复分支、改代码、push、`gh pr create`、Step D 评论），**无需**先单独走阶段零并等待用户对「解决规划」表态。**仅**指定单个 issue（如「解决 #123」）、且**未**要求「按优先级处理全部 / 扫描仓库」时，**可跳过阶段一～三**，从 **阶段四** Step A 起全量实现。

触发语示例：
- **`解决 #111`** / **`解决#111`**（`解决` 与 `#` 之间**可有空格也可无**；`#` 后为 issue 编号）/ `「解决 #123」` / `修 #123` / `处理 #123` / `搞定 #123`（口语里常省略 *issue* 一词）
- `"解决这个问题 https://github.com/.../issues/xxx"`
- `"请解决 https://github.com/.../issues/xxx"`
- `"解决 issue #xxx"`
- `"逐个解决 issues"`
- `"开始解决"`
- `"按照优先级解决所有 issues"`

> **解决前**：若该 issue 下已有 **`## 🔍 Issue 解读`** 评论，**先通读其中「可执行修复方案」** 再改代码；发起人通常已用该段内容**预览过**解决思路，实现应尽量与之对齐（除非代码审查中发现方案有误，再在 issue 中说明调整）。

> **分支优先（硬性）**：**在打开业务文件、编辑代码或执行任何 `git commit` 之前**，必须先完成 **从最新 `dev` 新建修复分支**（见下方「分支优先」与阶段四 Step A），且须在 **当前项目仓库根的主工作树**（`git rev-parse --show-toplevel`）内操作。**禁止**留在当前任意检出分支（如本地已 ahead 的 `dev`、无关 `feature/…` 等）上直接提交为解决该 issue 所作的改动。**不得**「先改完再开分支」；若误已在错误分支上 commit，须按用户要求 **revert** 或 **cherry-pick 到正确分支**，不得将无关提交混入 PR。

> **重要（完成定义）**：每个 issue（或每组相关 issues）解决完成后，**必须** `git push` 到远程并 **`gh pr create` 创建 Pull Request**（`--base dev`），供审阅与合并。**仅在本机 `git commit` 而未开 PR，不算完成**，须在对话结束前补齐 PR；若用户环境无法推送，须在回复中明确说明阻塞原因与待办（由谁 push / 开 PR）。

> **PR 要求**：标题与正文说明问题与改动；body 中使用 `Closes #xxx`（或 `Fixes`）关联 issue；创建后在对应 issue 下评论贴上 **PR 链接**（见 Step D）。

---

### 规划优先：两步走 + 阶段零（用户明确要求先解读 / 先规划时）

用户在**同一任务**中明示 **先不要写代码**、**先解读**、**解读完再做**、**先给方案**、**两步走**、**规划通过后再改** 等时，**必须**先完成 **第 1 步** 与下方 **阶段零 Step Z1～Z3**（只读 + 输出「解决规划」+ **等待用户确认**），**禁止**在此期间 `git checkout -b`、改业务代码、`git commit`。用户确认后进入 **第 2 步**：与「默认」路径相同——分支优先 + 全量实现（阶段一或阶段四～五）。

除用户改口为「直接改」「跳过规划」外，**不可**把第 1、2 步合并为一步。

| 步骤 | 做什么 | **禁止** |
|------|--------|----------|
| **第 1 步** | **需求分析**：读 issue、评论、截图；仓库内 **只读** 检索（`rg`、读文件、`gh issue view`）。在对话中输出 **解决方案**（问题摘要、根因假设、改动范围与主要路径、步骤、风险、验证方式）。 | **禁止** 修改业务代码、**禁止** `git checkout -b`、**禁止** `git commit`、**禁止** 写迁移/跑会改库的脚本（可读的 `gh` 查询除外）。 |
| **第 2 步** | **用户明确确认后**（如「可以开始」「通过」「按这个做」）：再执行「分支优先」与阶段一～五中的编码、push、PR、issue 评论等。 | — |

> **衔接**：第 1 步与 **阶段零**（Step Z1～Z3）同一套产出与停损规则；第 2 步从 **阶段零 Step Z4** 起进入阶段一或阶段四。

---

### 阶段零：解决规划与用户确认（仅规划优先路径）

**目的**：在创建分支、改代码、`git commit` 之前，与用户对齐解决方案；**仅在**上文「规划优先」适用时**必须**执行。**默认直接实现路径整段跳过。**

**进入条件**：用户已要求先解读 / 先规划 / 两步走 / 方案确认后再编码等。

**进入阶段一或阶段四之前（仅规划优先时）**：用户已触发规划优先时，**先完成**本阶段（含第 1 步：不写代码），再进入阶段一（批量扫描）或阶段四。

**可跳过本阶段**（转为直接实现，或从阶段四 Step A 起）：当且仅当用户已明确表达，例如：

- 「不用规划」「跳过规划」「直接改」「先写代码」
- 「按解读里的方案做」（且 issue 下已有 **`## 🔍 Issue 解读`** 且含可执行的「可执行修复方案」）
- 同一会话中用户已对该 issue 的规划表示通过（如「可以」「通过」「OK」「按这个来」）

#### Step Z1：阅读上下文

- 通读 issue 标题、body、评论与截图；若存在 **`## 🔍 Issue 解读`**，优先对齐其中的「可执行修复方案」。
- **读取截图**：若 issue 中有截图链接（`![...](url)`），**优先用 `playwright-cli open URL && playwright-cli screenshot --filename=/tmp/... && playwright-cli close` 在浏览器中打开再截图保存**，再用 Read 工具读取；这样可绕过 HTTP 500、签名过期、Referer 限制等问题，成功率高于 `curl` 或 WebFetch。
- 必要时在仓库内**只读**检索相关路径（`rg` / 阅读文件），**不**在此阶段大规模改写代码或执行迁移。
- **若 issue 描述不清晰、截图内容无法判断具体场景、或涉及业务规则需要确认**，**必须先向用户提问**，明确后再产出规划；不得凭猜测直接输出解决规划。

#### Step Z2：在对话中输出「解决规划」

建议包含（可按 issue 复杂度删减）：

| 区块 | 内容 |
|------|------|
| 问题摘要 | 现象与期望结果（一句话 + 要点） |
| 根因假设 | 若尚不确定，标注「待 Step B0 验证」 |
| 改动范围 | 模块、**主要文件路径（预估）** |
| 实施步骤 | 有序列表，具体到可执行 |
| 风险与注意 | API/多语言/迁移/兼容性等 |
| 验证方式 | 解决后如何确认 |
| PR 关联 | 说明本次 PR 准备用 `Closes #xxx` / `Fixes` 关联哪些编号；**勿写**未由本次改动实际解决的 issue |

#### Step Z3：等待用户确认（硬性，仅规划优先）

- 输出规划后，**明确停止**，并提示用户回复「通过」「可以开始」或提出修改意见。**本步对应「两步走」第 1 步结束**：此时仍属「只分析与方案」，**不得开始写代码**。
- **在用户确认前禁止**（与两步走第 1 步表格一致）：`git checkout -b`、修改业务代码、`git commit`、给 issue 打 `in-progress` 等「进入解决」动作（读取 issue、`gh issue view`、只读搜索除外）。
- 若用户要求调整规划，修订后再次等待确认。

#### Step Z4：用户通过后

用户表示同意后，再进入 **阶段一**（全仓库逐个解决）或 **阶段四**（单 issue 或已锁定的一组），且须从 **分支优先**（阶段四 Step A）开始，不得跳过从最新 `dev` 建分支的约定。

#### 与批量流程的衔接

- **阶段一～三**：**规划优先**下，若扫描结果会显著改变解决范围，应在进入阶段四前将**汇总结论 + 分组规划**写入对话并**再次**取得用户确认（若阶段零已覆盖则可简要确认「是否仍按此前规划执行」）。**默认直接实现**下，除非用户另有提示，可按扫描结果**继续分组并实现**，无需为多写一轮规划而刻意停顿。
- **阶段四第一组**：**规划优先**且尚无针对**该组**的规划共识时，先输出该组规划（或引用阶段零已通过的整体规划）并确认；若用户已在阶段零一次性批准「整体规划」，可逐组执行，**除非**某组与规划差异大须再对齐。**默认直接实现**下，读完本组 issues 后即可从 Step A 开工，除非用户要求先对齐方案。

---

### 主工作树（唯一）

本技能**不使用** `git worktree`。解决 issue 时的 **`git commit`、`git push`、打开业务文件编辑** 均在 **当前项目仓库根的主工作树**（`REPO_ROOT="$(git rev-parse --show-toplevel)"`）内完成：先 `cd "$REPO_ROOT"`，再按阶段四 Step A 从最新 `dev` 检出 `fix/...` 分支后继续。**禁止**在独立 `.worktrees/…` 目录中挂载副本；若本地曾因旧版技能留下 `.worktrees/`，可经用户确认后 `git worktree remove` / `git worktree prune` 清理，但**新建 issue 修复流程不再 `git worktree add`**。

---

### 阶段一：全量扫描与分类（批量「按优先级解决全部」等场景中，解决前统一执行；**单 issue 默认可跳过**）

**在需要跑全仓库优先级队列时**，先对所有待处理 issues 做一次完整扫描，产出分类结果，再按分类执行。用户**仅**说「解决 #N」且未要求全量扫仓时，**不必**执行本节，从 **阶段四** 起即可。

#### Step 0-A：获取全部待处理 issues

```bash
# 获取所有 open issues，按优先级排序
gh issue list --repo aotianlong/container-house --state open --limit 100 \
  --json number,title,labels,body \
  | python3 -c "
import sys, json
issues = json.load(sys.stdin)
priority = {'high-priority': 0, 'medium-priority': 1, 'low-priority': 2}
def pri(i):
    names = [l['name'] for l in i.get('labels', [])]
    return min((priority[n] for n in names if n in priority), default=3)
issues.sort(key=pri)
for i in issues:
    labels = [l['name'] for l in i.get('labels', [])]
    print(i['number'], '|', i['title'], '|', ','.join(labels))
"
```

#### Step 0-B：逐个检查 PR 关联状态

对每个 issue，通过 GitHub timeline API 检查是否已有关联 PR（timeline 比评论更可靠，能捕获所有 cross-reference）：

```bash
# 检查 issue 的 timeline，找关联的 PR 事件
gh api repos/aotianlong/container-house/issues/{number}/timeline \
  | python3 -c "
import sys, json
events = json.load(sys.stdin)
prs = []
for e in events:
    if e.get('event') in ('cross-referenced', 'referenced'):
        src = e.get('source', {})
        issue = src.get('issue', {})
        if issue.get('pull_request'):
            state = issue.get('state', 'unknown')
            merged = issue.get('pull_request', {}).get('merged_at')
            actual_state = 'merged' if merged else state
            prs.append(f'PR #{issue[\"number\"]} [{actual_state}]: {issue[\"title\"]}')
if prs:
    for p in prs: print(p)
else:
    print('无关联PR')
"
```

**判断规则**：
- `open` 或 `merged` 状态的关联 PR → 标记为 **跳过（已有PR）**
- `closed`（未合并）的关联 PR → 视为未解决，继续处理
- 无关联 PR → 继续处理

#### Step 0-C：预处理分类

对没有关联 PR 的 issues，逐个阅读标题、body、评论和截图，按以下标准分类：

| 分类 | 判断条件 | 后续操作 |
|------|----------|----------|
| ✅ **可解决** | 描述清晰，能定位到具体页面/功能，可推断复现路径 | 进入解决队列 |
| 📝 **需解读** | 只有一两句话，意图可理解但缺少结构化信息（无复现步骤/页面路径） | 先补充解读评论，再加入解决队列 |
| ❓ **待澄清** | 描述过于模糊，无法判断问题所在，且已有 `needs-clarification` 标签 → 跳过；无标签 → 打标签 + 评论 + 跳过 |

> **注意**：已有 `needs-clarification` 标签的 issue 说明上次已处理过，直接跳过，不重复评论。

> **重要**：此阶段只做**快速分类**，不做代码级别的验证。代码验证在阶段四 Step B0 中执行（每组开始解决前单独验证）。

#### Step 0-D：输出扫描结果汇总

扫描完成后，在对话中展示分类结果，格式如下：

```
📊 Issues 扫描结果
─────────────────────────────
✅ 可解决（进入解决队列）：
  #181 [高优先级] [租赁] 上传提箱单报错
  #155 [高优先级] [交易] 搜索后各Tab显示同一条记录
  ...

📝 需解读后解决：
  #210 任务通知页面通知需要中文显示
  ...

❓ 待澄清（已打标签，跳过）：
  #xxx 描述过于模糊的 issue

⏭️  跳过（已有关联PR）：
  #yyy 已有 PR #zzz [open]
─────────────────────────────
共 N 个待解决，M 个跳过，K 个待澄清
```

---

### 阶段二：预处理操作

#### 处理「需解读」的 issues

对分类为「需解读」的 issues，在解决前添加解读评论（复用解读流程的 Step R1～R5 格式），将简单描述扩展为结构化分析：

```bash
gh issue comment {ISSUE_NUMBER} --repo aotianlong/container-house --body "$(cat <<'EOF'
## 🔍 Issue 解读

### 问题理解

**现象**：（一句话）

**推断的复现路径**：
1. …
2. …

**期望行为**：…
**实际行为**：…
**相关页面**：`/path/to/page`

### 根因初步分析

（引用相关代码路径，说明可能原因）

### 相似 / 关联 OPEN issue

（先做 Step R2.5：`gh search issues` / `gh issue list`；无则写「未发现明显重叠的 OPEN issue」）

### 可执行修复方案（供实现与预览）

**改动清单**：
1. `path/to/file` — 具体改什么（足够让 AI 直接下手）
2. …

### 验证方式

（解决后如何确认）

（若信息仍不足，在方案中明确列出**仍缺什么**并建议打 `needs-clarification`，勿编造实现细节）
EOF
)"
```

#### 处理「待澄清」的 issues

**Step 1：确保 `needs-clarification` 标签存在**

```bash
gh label list --repo aotianlong/container-house --json name \
  | python3 -c "
import sys, json
labels = [l['name'] for l in json.load(sys.stdin)]
exit(0 if 'needs-clarification' in labels else 1)
" || gh label create "needs-clarification" \
     --repo aotianlong/container-house \
     --color "e4e669" \
     --description "描述不清晰，需要补充信息"
```

**Step 2：打标签 + 添加评论**

```bash
gh issue edit {ISSUE_NUMBER} --repo aotianlong/container-house --add-label "needs-clarification"

gh issue comment {ISSUE_NUMBER} --repo aotianlong/container-house --body "$(cat <<'EOF'
## ❓ 需要补充信息

当前描述不够清晰，无法定位问题。请补充以下信息：

- **具体在哪个页面？**（URL 或页面路径）
- **完整的复现步骤是什么？**
- **期望的行为是什么？**
- **实际看到的现象是什么？**（如有截图或错误信息，请附上）
- **相关的订单号/用户账号？**（如适用）

感谢配合！
EOF
)"
```

---

### 阶段三：分组规划

对解决队列中的 issues（包括「可解决」和「需解读后解决」），按模块/文件分组：

**分组原则**：
- 同一页面或功能模块的 issues → 合并到一个分支
- 涉及不同模块但文件不重叠的 issues → 可合并（减少 PR 数量）
- 涉及数据库迁移或服务器操作的 → 单独一个分支
- 每个分支对应一个 PR，分支命名：`fix/{issue1}-{issue2}-...`

---

### 阶段四：逐组解决

对每组 issues，按以下步骤执行：

#### 分支优先（执行顺序）

1. **先**完成下方 Step A：在**仓库根主工作树**内 `fetch`/`pull` 最新 `dev`，再 `checkout -b fix/…`，然后打 `in-progress` 标签。
2. **再**进行 Step B0 及之后的验证与代码修改、`git commit`（当前目录即为仓库根下的修复分支工作区）。

若跳过 Step A 已开始改代码，**立即停下**：保存或 stash 改动 → 执行 Step A → 再应用改动。

#### Step A：创建分支并打 in-progress 标签

**确保 `in-progress` 标签存在**：

```bash
gh label list --repo aotianlong/container-house --json name \
  | python3 -c "
import sys, json
labels = [l['name'] for l in json.load(sys.stdin)]
exit(0 if 'in-progress' in labels else 1)
" || gh label create "in-progress" \
     --repo aotianlong/container-house \
     --color "0075ca" \
     --description "正在解决 issue 中"
```

**A. 从 dev 创建分支（主工作树，唯一路径）**

须在与 issue 无关的干净起点上创建；先 `fetch`/`pull` 保证基于最新 `origin/dev`，且**不要**把非本 issue 的提交算进本分支。

将 `{issue-numbers}` 替换为实际编号（如 `123` 或 `123-456`），分支名为 `fix/{issue-numbers}`。

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
git fetch origin dev
git checkout dev && git pull origin dev
git checkout -b "fix/{issue-numbers}"
```

> **禁止**：在 `git checkout -b` 之前对业务代码做任何修改或 `git commit`（读取 issue、运行 `gh issue view` 等除外）。

**给本组所有 issue 打 `in-progress` 标签**：

```bash
gh issue edit {ISSUE_NUMBER} --repo aotianlong/container-house --add-label "in-progress"
```

#### Step B0：验证问题是否仍然存在

**在动手修改代码之前**，先确认问题在当前代码库中是否仍然存在。有些 issue 可能已经在其他 PR 中被顺带解决，或者是数据问题而非代码问题。

**验证方法（按顺序尝试）**：

1. **查看 git log**：搜索是否有相关提交已解决此问题

```bash
# 搜索近期提交是否涉及相关文件或关键词
git log --oneline -50 --all | head -50
git log --oneline --all -- path/to/related/file.rb | head -10
```

2. **直接检查代码**：根据 issue 描述，找到相关代码，判断问题是否仍然存在

```bash
# 根据错误信息或功能描述，在代码中搜索相关逻辑
rg "相关关键词" app/ web2/src/
```

3. **检查测试服务器**（可选，仅当代码检查不确定时）：
   - 如果 issue 有具体的 URL，用浏览器工具访问测试服务器验证
   - 如果有具体的 API 错误，可以用 curl 测试 API 端点

**判断结果**：

| 结论 | 处理方式 |
|------|----------|
| ✅ **问题仍然存在** | 继续 Step B，落实解决方案 |
| ✅ **问题已被解决**（代码中已有相关改动） | 在 issue 添加评论说明，关闭 issue，跳过此组 |
| ⚠️ **无法确认**（需要运行时验证） | 简要说明情况，继续解决（宁可重复处理也不漏掉） |

**已解决时的评论模板**：

```bash
gh issue comment {ISSUE_NUMBER} --repo aotianlong/container-house --body "$(cat <<'EOF'
## ✅ 问题已在代码中解决

经过代码检查，此问题已在近期的提交中得到解决：

- **相关提交**：`commit-hash` — 提交说明
- **涉及文件**：`path/to/file`

无需额外处理，关闭此 issue。
EOF
)"
gh issue close {ISSUE_NUMBER} --repo aotianlong/container-house
```

---

#### Step B：落实解决方案

在代码库中定位相关文件，落实解决方案。commit 信息格式：

```
fix: 问题简述

解决 #xxx 和 #yyy：
- 具体改动说明
- 根本原因说明
```

#### Step C：推送并创建 PR（审阅前置步骤，必做）

从远程分支发起 PR，便于 Reviewer 在 GitHub 上 diff、留言、批准合并。

```bash
git push -u origin "fix/{issue-numbers}"
gh pr create \
  --title "fix: 标题 (#xxx #yyy)" \
  --base dev \
  --body "$(cat <<'EOF'
## 问题描述
...

## 根本原因
...

## 解决方案
...

Closes #xxx
Closes #yyy
EOF
)"
```

- **单条 issue 解决**：同样走独立分支 + PR，勿把「已 commit 到 dev」当作交付终点（除非用户明确要求不建 PR）。
- PR 创建成功后，移除本组所有 issue 的 `in-progress` 标签：

```bash
gh issue edit {ISSUE_NUMBER} --repo aotianlong/container-house --remove-label "in-progress"
```

#### Step D：在 Issue 中写解决总结

每个 issue 添加评论：

```bash
gh issue comment {ISSUE_NUMBER} --repo aotianlong/container-house --body "$(cat <<'EOF'
## ✅ 解决说明

**根本原因**：...

**改动摘要**：
- `path/to/file` — 具体改动

**PR**：https://github.com/aotianlong/container-house/pull/{PR_NUMBER}
EOF
)"
```

#### Step E：继续下一组

完成一组后，回到阶段四 Step A，处理下一组。

---

### 阶段五：完成汇总

所有组处理完毕后，输出最终汇总：

```
✅ 解决完成汇总
─────────────────────────────
已解决（PR 已创建）：
  #181 → PR #xxx
  #155 → PR #yyy
  ...

⏭️  跳过（已有PR）：
  #zzz → 已有 PR #www [merged]

❓ 待澄清（已通知）：
  #aaa 已打 needs-clarification 标签
─────────────────────────────
```

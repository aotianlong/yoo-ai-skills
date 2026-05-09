---
name: github-issues
description: **执行本技能前：先在对话中提出计划（范围、主要步骤、将创建/发布内容的摘要或草案），明确等待用户确认后再执行**；用户已说「直接执行」「跳过规划」等可例外。将 Word 文档（.docx）中的问题/需求截图分析后，批量创建为 GitHub Issues，附带截图和来源文档链接。当用户说"把 xx 文件转换成 issues"、"从文档创建 issues"、"把文档发布到 github" 时自动应用。创建完 issues 后，当用户要求"逐个解决 issues"时，为每组相关 issues 创建独立分支修复；**修复完成后必须 push 并创建 PR（目标分支一般为 dev）供代码审阅，禁止仅本地 commit 即视为完成**；并在各 issue 评论中写解决过程总结与 PR 链接。**父 issue + 子 issue / Epic**：见 `includes/07-sub-issues.md`——只读阶段须列出子任务与关闭策略，默认勿对未完成的子任务集误 `Closes #父`。**解决具体编号 issue（触发本技能）**：当用户说 **「解决 #111」**、**「解决#111」**、**「解决 #123」** 等（`解决` 与 `#` 之间可有可无空格，`#` 后为 issue 编号）、**「修 #xxx」「处理 #xxx」「搞定 #xxx」**、或带 issue URL /「解决 issue #xxx」时，**必须采用固定两步走**——**第一步**：只做需求理解与只读分析，在对话中输出解决方案（范围、步骤、风险、验证），**此步禁止写代码、禁止 `git checkout -b`、禁止 `git worktree add`、禁止 commit**；**第二步**：仅在用户明确确认（如「可以开始」「通过」「按这个做」）后，再进入建分支与编码、PR 等环节（见 `includes/03-issue-fix.md`「阶段零」与「两步走」）；带 **issue URL**（如「解决这个问题 https://…/issues/n」）同此。**用户确认、进入编码阶段后**：须从最新 `dev` 新建修复分支（见 `includes/03-issue-fix.md`「分支优先」），禁止在当前检出分支上直接 commit，**结束时必须创建 PR**。**默认工作目录**：在**主仓库根**下用 `git worktree` 检出到 **`.worktrees/wt-{issue-id}`**（同组多 issue 用 `wt-111-222` 与分支编号顺序一致）；**`gh pr create` 成功后**回到主仓库执行 `git worktree remove` 删除该目录。用户明确说 **不用 worktree / 不用 worktree 模式 / 在当前目录（主工作树）做** 等时，**不要**建 worktree，沿用原「`cd` 到主仓库再 `checkout -b`」流程。当用户说"帮我添加 issue"、"帮我创建 issue"、"新建一个 issue"、"添加一个需求"、"提一个 bug" 等时，进入口述需求创建 Issue 流程。当用户说"解读 issue"、"分析 issue"、"帮我看看这个 issue"、"解析所有 issues"、"批量解读"、"跳过已解读"、"解读一下 #xxx"、"解读 #xxx"、"看一下 #xxx"、"分析 #xxx"、"解读这个 #xxx"、"帮我解读 #xxx"（其中 xxx 为 issue 编号）等时，进入 Issue 解读流程（**仅 OPEN**；须**检索类似 OPEN issue**（Step R2.5）并写入解读；解读正文须含**可落地修复方案**；**解读后 Step R6 仅追加标签**，已有标签视为故意、禁止覆盖；**发帖前须在对话中展示拟发布全文并经用户确认**（见 `includes/02-issue-interpretation.md` Step R5）。单条走 Step R1～R6；批量见「批量解读与全仓库扫描」），经确认后必须写入 issue 评论（或运行本技能目录下脚本发帖）。
---

# Doc to GitHub Issues

将 `.docx` 文档中的截图和标注分析后，批量创建带标签、截图、来源文档的 GitHub Issues。详细步骤已按功能拆到 **`includes/`** 下，**按任务只打开对应文件**即可。

## 按功能引用（includes）

| 场景 | 打开 |
|------|------|
| 前置条件、测试环境 URL | [`includes/00-common.md`](includes/00-common.md) |
| 从 Word 批量创建 Issues（Step 0 计划与确认 + 1～10） | [`includes/01-docx-to-issues.md`](includes/01-docx-to-issues.md) |
| Issue 解读、批量扫描/发帖、R1～R6（含解读后打标签） | [`includes/02-issue-interpretation.md`](includes/02-issue-interpretation.md) |
| Issue 修复、**两步走**、**阶段零（规划与用户确认）**、分支、PR、阶段一至五 | [`includes/03-issue-fix.md`](includes/03-issue-fix.md) |
| 口述需求创建 Issue（Step V0 计划与确认 + V1～V6） | [`includes/04-voice-create-issue.md`](includes/04-voice-create-issue.md) |
| 标签表、防重复规则、注意事项 | [`includes/05-reference.md`](includes/05-reference.md) |
| PR 审核、Approve、Request Changes | [`includes/06-pr-review.md`](includes/06-pr-review.md) |
| **子 issue / 父 Epic**（列出子任务、关闭策略、PR 关键词） | [`includes/07-sub-issues.md`](includes/07-sub-issues.md) |

## 脚本

| 脚本 | 说明 |
|------|------|
| [`scripts/scan_issue_interpretation_status.py`](scripts/scan_issue_interpretation_status.py) | 扫描 OPEN 中谁还缺「Issue 解读」 |
| [`scripts/post_open_issue_interpretations.py`](scripts/post_open_issue_interpretations.py) | 按内置字典批量发帖（OPEN + 防重复） |
| [`scripts/append_new_spec_interpret_comments.py`](scripts/append_new_spec_interpret_comments.py) | 向全部 OPEN 追加「新规范补充」解读（幂等） |

## 给 AI 的指引

0. **先规划、后执行（本技能总规则）**：凡将调用 `gh` 创建/编辑 issue、发评论、跑发帖脚本、上传资源并批量建 issue 等，**应先在对话中说明计划**（例如：将处理哪份文档、预计几条 issue 及标题/标签草案、或解读帖的发布范围与一条样例全文），**待用户明确确认**（如「可以」「按这个执行」「发吧」）后再动手。仅只读帮助（如帮查 `gh issue list`、解释某条 issue 且不改 GitHub）可不经确认。用户已说「直接执行」「不用确认」「跳过规划」等则视为豁免。
1. 根据用户意图**精读上表中对应的 include 文件**，不必默认读完所有分片。
2. 任务跨多阶段时（例如「先解读 #155 再修复」），依次打开 `02-issue-interpretation.md` 与 `03-issue-fix.md`。
3. 创建 issue 选标签时查阅 `05-reference.md`。
4. **解读 issue 后**按 `02` 中 Step R6 **只追加**标签；**已有标签不删不改**（细则见 `05-reference.md`「解读后打标签规则」）。
5. **修复 issue 前（默认，含「解决 #xxx」类请求）**：按 `03` 中「两步走 / 阶段零」**先**完成需求分析与方案（**不写代码**），**再**等用户确认后才开始改动；用户已说「直接改」「跳过规划」等时可跳过。**若 issue 描述不清晰或有不确定之处，必须先向用户提问再规划**，不得猜测后直接编码。
6. **修复 issue 后**：按 `03` 完成 **push + `gh pr create`（base `dev`）**；在 issue 评论中写总结并附 PR 链接。**不得**在仅本地提交后结束任务（无法推送时须说明原因）。**默认**用 **`git worktree`** 在 **`.worktrees/wt-{issue-id}`** 内编码；PR 创建成功后 **`git worktree remove`** 清理。用户说不用 worktree 时跳过此模式（细则见 `03`「Worktree 模式」）。
7. **审核 PR 时**：精读 `06-pr-review.md`；若发现 🔴 必须修复问题，先帮用户修复代码并 push，再执行 Approve；无阻塞问题则直接 Approve。
8. **父 issue、子 issue、Epic**：在「解决 #xxx」「解读 #xxx」等流程的**只读阶段**，若发现正文/评论中有子任务编号或父任务引用，**按 `07-sub-issues.md`** 汇总子 issue 状态、界定本次交付范围、明确是否/何时 `Closes #父`，避免误关或遗漏。

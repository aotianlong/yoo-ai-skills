---
name: github-issues
description: **执行本技能前：先在对话中提出计划（范围、主要步骤、将创建/发布内容的摘要或草案），明确等待用户确认后再执行**；用户已说「直接执行」「跳过规划」等可例外。**列出/查看 Issues（只读）**：当用户说「列出 issues」「issue 列表」「有哪些 open issue」「按标签/负责人筛 issues」等时，按 `includes/07-list-issues.md` 使用 `gh issue list` / `gh issue view`，可不经确认。**GitHub Gist**：当用户说「创建/列出/查看/编辑/删除 gist」「gist 克隆」等时，按 `includes/09-github-gist.md` 使用 `gh gist`；其中 **list/view 只读可不经确认**；**create/edit/delete/rename/clone（写本地）** 须先说明计划并征得确认，用户已说「直接执行」「跳过规划」等除外。将 Word 文档（.docx）中的问题/需求截图分析后，批量创建为 GitHub Issues，附带截图和来源文档链接。当用户说"把 xx 文件转换成 issues"、"从文档创建 issues"、"把文档发布到 github" 时自动应用。创建完 issues 后，当用户要求"逐个解决 issues"时，为每组相关 issues 创建独立分支以解决对应 issue；**解决完成后必须 push 并创建 PR（目标分支一般为 dev）供代码审阅，禁止仅本地 commit 即视为完成**；并在各 issue 评论中写解决过程总结与 PR 链接。**合并 GitHub PR**：当用户说「合并 PR」「merge PR」「把 PR #xxx 合进去」等时，按 `includes/08-pr-merge.md`**先查是否已合并**、必要时**解决冲突**再 `gh pr merge`，合并后**校验并关闭关联 issue**。**解决具体编号 issue（触发本技能）**：当用户说 **「解决 #111」**、**「解决#111」**、**「解决 #123」** 等、`修 #xxx`、**「处理 #xxx」「搞定 #xxx」**、或带 issue URL /「解决 issue #xxx」时：**默认不强制「先给规划再等确认」**——若用户**未**在同一任务中要求 **先解读 / 先分析再改 / 只规划不写代码 / 两步走 / 方案通过再说** 等，则在读完 issue、必要时只读检索后，**直接进入** `03` 中的分支、编码、push、PR、issue 评论等**全量实现流程**；**若用户明确要求先解读或先规划**，则按 `03` 的「规划优先（两步走）+ 阶段零」执行：**第 1 步**仅只读分析与输出方案（禁止写代码、`git checkout -b`、commit），**第 2 步**待用户确认后再编码。带 **issue URL** 同此。**用户确认、进入编码阶段后**：须 `cd` 到**当前项目仓库根**（`git rev-parse --show-toplevel`），从最新 `dev` 新建修复分支（见 `includes/03-issue-fix.md`「分支优先」），在**主工作树**内完成编码与提交；禁止在错误的检出分支上直接 commit 本 issue 的改动，**结束时必须创建 PR**。**不使用** `git worktree`，始终在单一工作树中操作。当用户说"帮我添加 issue"、"帮我创建 issue"、"新建一个 issue"、"添加一个需求"、"提一个 bug" 等时，进入口述需求创建 Issue 流程。当用户说"解读 issue"、"分析 issue"、"帮我看看这个 issue"、"解析所有 issues"、"批量解读"、"跳过已解读"、"解读一下 #xxx"、"解读 #xxx"、"看一下 #xxx"、"分析 #xxx"、"解读这个 #xxx"、"帮我解读 #xxx"（其中 xxx 为 issue 编号）等时，进入 Issue 解读流程（**仅 OPEN**；须**检索类似 OPEN issue**（Step R2.5）并写入解读；解读正文须含**可落地修复方案**；**解读后 Step R6 仅追加标签**，已有标签视为故意、禁止覆盖；**发帖前须在对话中展示拟发布全文并经用户确认**（见 `includes/02-issue-interpretation.md` Step R5）。单条走 Step R1～R6；批量见「批量解读与全仓库扫描」），经确认后必须写入 issue 评论（或运行本技能目录下脚本发帖）。
---

# Doc to GitHub Issues

将 `.docx` 文档中的截图和标注分析后，批量创建带标签、截图、来源文档的 GitHub Issues。详细步骤已按功能拆到 **`includes/`** 下，**按任务只打开对应文件**即可。

## 按功能引用（includes）

| 场景 | 打开 |
|------|------|
| 前置条件、测试环境 URL | [`includes/00-common.md`](includes/00-common.md) |
| 从 Word 批量创建 Issues（Step 0 计划与确认 + 1～10） | [`includes/01-docx-to-issues.md`](includes/01-docx-to-issues.md) |
| Issue 解读、批量扫描/发帖、R1～R6（含解读后打标签） | [`includes/02-issue-interpretation.md`](includes/02-issue-interpretation.md) |
| Issue 解决、**默认直接全量实现**、**规划优先（可选）**、分支、PR、阶段一至五 | [`includes/03-issue-fix.md`](includes/03-issue-fix.md) |
| 口述需求创建 Issue（Step V0 计划与确认 + V1～V6） | [`includes/04-voice-create-issue.md`](includes/04-voice-create-issue.md) |
| 标签表、防重复规则、注意事项 | [`includes/05-reference.md`](includes/05-reference.md) |
| PR 审核、Approve、Request Changes | [`includes/06-pr-review.md`](includes/06-pr-review.md) |
| **列出 / 筛选 Issues**（`gh issue list`，只读） | [`includes/07-list-issues.md`](includes/07-list-issues.md) |
| **合并 PR**（是否已合并、冲突解决、`gh pr merge`、关闭关联 issue） | [`includes/08-pr-merge.md`](includes/08-pr-merge.md) |
| **GitHub Gist**（`gh gist`：列出、查看、创建、编辑、删除、重命名、克隆） | [`includes/09-github-gist.md`](includes/09-github-gist.md) |

## 脚本

| 脚本 | 说明 |
|------|------|
| [`scripts/scan_issue_interpretation_status.py`](scripts/scan_issue_interpretation_status.py) | 扫描 OPEN 中谁还缺「Issue 解读」 |
| [`scripts/post_open_issue_interpretations.py`](scripts/post_open_issue_interpretations.py) | 按内置字典批量发帖（OPEN + 防重复） |
| [`scripts/append_new_spec_interpret_comments.py`](scripts/append_new_spec_interpret_comments.py) | 向全部 OPEN 追加「新规范补充」解读（幂等） |

## 给 AI 的指引

0. **先规划、后执行（本技能总规则）**：凡将调用 `gh` 创建/编辑 issue、发评论、跑发帖脚本、上传资源并批量建 issue 等，**应先在对话中说明计划**（例如：将处理哪份文档、预计几条 issue 及标题/标签草案、或解读帖的发布范围与一条样例全文），**待用户明确确认**（如「可以」「按这个执行」「发吧」）后再动手。**Gist**：`gh gist create` / `edit` / `delete` / `rename` / `clone` 等会**变更 GitHub 或本地目录**，同上须确认，细则见 **`09-github-gist.md`**。仅只读帮助（如 `gh issue list`、`gh gist list`、`gh gist view`、`gh issue view`、解释内容且不改远端）可不经确认。用户已说「直接执行」「不用确认」「跳过规划」等则视为豁免。
1. 根据用户意图**精读上表中对应的 include 文件**，不必默认读完所有分片。用户只要**罗列或筛选** issues 时，打开 **`07-list-issues.md`**；**管理 Gist** 时打开 **`09-github-gist.md`**。
2. 任务跨多阶段时（例如「先解读 #155 再解决」），依次打开 `02-issue-interpretation.md` 与 `03-issue-fix.md`。
3. 创建 issue 选标签时查阅 `05-reference.md`。
4. **解读 issue 后**按 `02` 中 Step R6 **只追加**标签；**已有标签不删不改**（细则见 `05-reference.md`「解读后打标签规则」）。
5. **解决 issue**：用户**未**要求先解读/先规划/两步走时，按 `03` **直接**进入分支与全量实现（读 issue、必要只读检索后即编码、PR）；用户**明确要求**先解读、先给方案再改、只分析、两步走等时，按 `03`「规划优先」**先**完成分析与方案并**待确认**后再改动。**若 issue 不清晰，任何路径下均须先提问**，不得猜测后硬编码。
6. **解决 issue 后**：按 `03` 完成 **push + `gh pr create`（base `dev`）**；在 issue 评论中写总结并附 PR 链接。**不得**在仅本地提交后结束任务（无法推送时须说明原因）。**始终在仓库根主工作树**内编码与提交（细则见 `03`「主工作树」）。
7. **审核 PR 时**：精读 `06-pr-review.md`；若发现 🔴 必须修复问题，先帮用户修复代码并 push，再执行 Approve；无阻塞问题则直接 Approve。
8. **合并 PR 时**：精读 `08-pr-merge.md`；**先**用 `gh pr view --json mergedAt` 判断是否已合并；有冲突则按该文件合并 base、解决后 push，再 `gh pr merge`；合并后根据 `closingIssuesReferences` 校验，对仍 OPEN 的关联 issue 执行 `gh issue close` 并评论说明。

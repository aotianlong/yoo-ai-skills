---
name: github-issues
description: **执行本技能前：先在对话中提出计划（范围、主要步骤、将创建/发布内容的摘要或草案），明确等待用户确认后再执行**；用户已说「直接执行」「跳过规划」等可例外。将 Word 文档（.docx）中的问题/需求截图分析后，批量创建为 GitHub Issues，附带截图和来源文档链接。**读取 issue 图片/附件**（`user-attachments` 须 `gh auth token` + curl，见 `includes/10-read-issue-attachments.md`）。**列出/查看 Issues（只读）**：「列出 issues」「按标签筛」等 → `includes/07-list-issues.md`。**GitHub Gist**：`includes/09-github-gist.md`；写操作默认先规划再执行。**解决 #xxx**：**两步走**——第 1 步只读分析与修复规划（禁止写代码/commit）；第 2 步用户确认后从 `dev` 建分支、编码、**push + `gh pr create`（base `dev`）**、issue 评论附 PR 链接（见 `includes/03-issue-fix.md` 阶段零）。**解读 issue**：发帖前须在对话展示拟发布全文并经用户确认（`02` Step R5）。Word 建 issue、口述建 issue 见 `01`/`04` Step 0 / V0。合并 PR、审核 PR 见 `06`/`08`。**编码**：仓库根主工作树，不用 `git worktree`。
---

# Doc to GitHub Issues

将 `.docx` 文档中的截图和标注分析后，批量创建带标签、截图、来源文档的 GitHub Issues。详细步骤已按功能拆到 **`includes/`** 下，**按任务只打开对应文件**即可。

## 先规划，再执行（默认总流程）

凡会改动 GitHub、上传资源或修改仓库的操作，**默认两阶段**：

1. **规划（阶段 A）**：只读分析 → 在对话中输出计划/方案/草案 → **停止并等待用户确认**
2. **执行（阶段 B）**：用户确认后，再 `gh` 发帖/建 issue、改代码、commit、push、开 PR 等

细则见 **[`includes/00-plan-then-execute.md`](includes/00-plan-then-execute.md)**。子流程内的 Step 0 / 阶段零 / Step V0 / Step R5 预览均属阶段 A。

用户说「直接执行」「跳过规划」「直接改」「发吧」等 → 可跳过阶段 A。仅 `gh issue list/view`、列出 Gist 等只读帮助 → 无需确认。

## 按功能引用（includes）

| 场景 | 打开 |
|------|------|
| **先规划再执行（总纲，默认必读）** | [`includes/00-plan-then-execute.md`](includes/00-plan-then-execute.md) |
| 前置条件、测试环境 URL | [`includes/00-common.md`](includes/00-common.md) |
| 从 Word 批量创建 Issues（Step 0 计划与确认 + 1～10） | [`includes/01-docx-to-issues.md`](includes/01-docx-to-issues.md) |
| Issue 解读、批量扫描/发帖、R1～R6（含解读后打标签） | [`includes/02-issue-interpretation.md`](includes/02-issue-interpretation.md) |
| Issue 解决、**两步走**、**阶段零（规划与用户确认）**、分支、PR、阶段一至五 | [`includes/03-issue-fix.md`](includes/03-issue-fix.md) |
| 口述需求创建 Issue（Step V0 计划与确认 + V1～V6） | [`includes/04-voice-create-issue.md`](includes/04-voice-create-issue.md) |
| 标签表、防重复规则、注意事项 | [`includes/05-reference.md`](includes/05-reference.md) |
| PR 审核、Approve、Request Changes | [`includes/06-pr-review.md`](includes/06-pr-review.md) |
| **列出 / 筛选 Issues**（`gh issue list`，只读） | [`includes/07-list-issues.md`](includes/07-list-issues.md) |
| **合并 PR**（是否已合并、冲突解决、`gh pr merge`、关闭关联 issue） | [`includes/08-pr-merge.md`](includes/08-pr-merge.md) |
| **GitHub Gist**（`gh gist`：列出、查看、创建、编辑、删除、重命名、克隆） | [`includes/09-github-gist.md`](includes/09-github-gist.md) |
| **读取 issue 图片/附件**（`user-attachments` 须 `gh` token） | [`includes/10-read-issue-attachments.md`](includes/10-read-issue-attachments.md) |

## 脚本

| 脚本 | 说明 |
|------|------|
| [`scripts/download_issue_attachments.sh`](scripts/download_issue_attachments.sh) | 拉取 issue 正文/评论中的图片与附件到 `/tmp/issue-<n>-attachments/` |
| [`scripts/scan_issue_interpretation_status.py`](scripts/scan_issue_interpretation_status.py) | 扫描 OPEN 中谁还缺「Issue 解读」 |
| [`scripts/post_open_issue_interpretations.py`](scripts/post_open_issue_interpretations.py) | 按内置字典批量发帖（OPEN + 防重复） |
| [`scripts/append_new_spec_interpret_comments.py`](scripts/append_new_spec_interpret_comments.py) | 向全部 OPEN 追加「新规范补充」解读（幂等） |

## 给 AI 的指引

0. **先规划、后执行（本技能总规则）**：动手前**先读 [`00-plan-then-execute.md`](includes/00-plan-then-execute.md)**，按两阶段执行——阶段 A 只输出计划/草案并等确认，阶段 B 再调用 `gh`、改代码、push、开 PR。用户已说「直接执行」「跳过规划」等则豁免。
1. 根据用户意图**精读上表中对应的 include 文件**（写操作默认含 `00-plan-then-execute.md`），不必默认读完所有分片。用户只要**罗列或筛选** issues 时，打开 **`07-list-issues.md`**；**管理 Gist** 时打开 **`09-github-gist.md`**。
2. **issue 含截图或 `user-attachments` 附件时**：必读 [`includes/10-read-issue-attachments.md`](includes/10-read-issue-attachments.md)；**禁止**因裸 `curl`/`WebFetch` 404 就判定读不到图。
3. 任务跨多阶段时（例如「先解读 #155 再解决」），依次打开 `02-issue-interpretation.md` 与 `03-issue-fix.md`。
4. 创建 issue 选标签时查阅 `05-reference.md`。
5. **解读 issue 后**按 `02` 中 Step R6 **只追加**标签；**已有标签不删不改**（细则见 `05-reference.md`「解读后打标签规则」）。
6. **解决 issue 前（默认，含「解决 #xxx」）**：按 `03`「两步走 / 阶段零」**先**完成需求分析与修复规划（**不写代码**），**再**等用户确认后建分支、编码、开 PR；用户已说「直接改」「跳过规划」等时可跳过。issue 不清晰须先提问。
7. **解决 issue 后**：按 `03` 完成 **push + `gh pr create`（base `dev`）**；在 issue 评论中写总结并附 PR 链接，且**必须**写入本次 **AI 会话 ID** 与 transcript 路径（细则见 `00-common.md`、`03` Step D）。**始终在仓库根主工作树**内编码与提交。
8. **审核 PR 时**：精读 `06-pr-review.md`；若发现 🔴 必须修复问题，先帮用户修复代码并 push，再执行 Approve；无阻塞问题则直接 Approve。
9. **合并 PR 时**：精读 `08-pr-merge.md`；**先**用 `gh pr view --json mergedAt` 判断是否已合并；有冲突则按该文件合并 base、解决后 push，再 `gh pr merge`；合并后根据 `closingIssuesReferences` 校验，对仍 OPEN 的关联 issue 执行 `gh issue close` 并评论说明。

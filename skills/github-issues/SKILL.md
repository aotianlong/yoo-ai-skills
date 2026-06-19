---
name: github-issues
description: >
  **默认直接执行**：创建/编辑 issue、发帖、`gist` 写操作、从文档批量建 issue、「解决 #xxx」等，参数与意图清楚则**立刻动手**。**读取 issue 图片/附件**（`user-attachments` 须 `gh auth token` + curl，见 `includes/10-read-issue-attachments.md`）。可落地的修改路径写在 issue **`## 🔍 Issue 解读`**（**解读贴**）；若要调整方向，在 issue 上追加或修订评论。**列出/查看 Issues（只读）**：「列出 issues」「按标签筛」等 → `includes/07-list-issues.md`、`gh issue list` / `gh issue view`。**GitHub Gist**：`includes/09-github-gist.md`、`gh gist`；list/view 只读；create/edit/delete/rename/clone **默认直接执行**，参数不全或用户要求先发预览时再停顿。Word（.docx）批量建 issue、口述建 issue、合并 PR、审核 PR 等均按对应 include。逐个解决 issues：**必须 push + `gh pr create`（base `dev`）**，禁止仅本地 commit；issue 评论附 PR 链接。**解决 #xxx / issue URL**：通读 issue、评论及已有解读贴（若有），按「可执行修复方案」或自拟等价方案，**直接**走 `03` 分支→编码→PR→评论。「先解读再解决」：先发 `02` Step R5，**随即**接 `03`。用户明示「只解读 / 别写代码」：仅 `02`。含糊、缺编号、或用户**要求先看草案**时再停顿。**编码**：仓库根主工作树、`dev` 建新分支（见 `03`），**必须 PR**，不用 `git worktree`。解读触发语 → `02`（OPEN、R2.5、可落地方案、R6 只追加标签、默认 `gh issue comment`，Step R5）。
---

# Doc to GitHub Issues

将 `.docx` 文档中的截图和标注分析后，批量创建带标签、截图、来源文档的 GitHub Issues。详细步骤已按功能拆到 **`includes/`** 下，**按任务只打开对应文件**即可。

## 按功能引用（includes）

| 场景 | 打开 |
|------|------|
| 前置条件、测试环境 URL | [`includes/00-common.md`](includes/00-common.md) |
| 从 Word 批量创建 Issues（Step 0 简述与直接执行 + 1～10） | [`includes/01-docx-to-issues.md`](includes/01-docx-to-issues.md) |
| Issue 解读、批量扫描/发帖、R1～R6（含解读后打标签） | [`includes/02-issue-interpretation.md`](includes/02-issue-interpretation.md) |
| Issue 解决、**默认按解读贴/上下文直接全量实现**、分支、PR、阶段一至五 | [`includes/03-issue-fix.md`](includes/03-issue-fix.md) |
| 口述需求创建 Issue（Step V0 简述 + V1～V6） | [`includes/04-voice-create-issue.md`](includes/04-voice-create-issue.md) |
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

0. **默认直接执行**：写操作（`gh issue`、`gist` 发帖/创建等）在参数与意图明确时**立即执行**；同条回复可两三句交代范围。仅当仓库/编号不明、需求含糊、或用户**要求先审预览**时停顿。
1. 根据用户意图**精读上表中对应的 include 文件**，不必默认读完所有分片。用户只要**罗列或筛选** issues 时，打开 **`07-list-issues.md`**；**管理 Gist** 时打开 **`09-github-gist.md`**。
2. **issue 含截图或 `user-attachments` 附件时**：必读 [`includes/10-read-issue-attachments.md`](includes/10-read-issue-attachments.md)；**禁止**因裸 `curl`/`WebFetch` 404 就判定读不到图。
3. 任务跨多阶段时（例如「先解读 #155 再解决」），依次打开 `02-issue-interpretation.md` 与 `03-issue-fix.md`。
4. 创建 issue 选标签时查阅 `05-reference.md`。
5. **解读 issue 后**按 `02` 中 Step R6 **只追加**标签；**已有标签不删不改**（细则见 `05-reference.md`「解读后打标签规则」）。
6. **解决 issue**：按 `03`，读完 issue、解读贴（若有）、**按 `10` 读取截图/附件**、做完必要只读检索后**直接**分支、编码、PR；方案写在解读贴。「先解读再解决」：发帖后立即续跑 `03`。明示只要解读则仅 `02`。issue 不清晰须先提问。
7. **解决 issue 后**：按 `03` 完成 **push + `gh pr create`（base `dev`）**；在 issue 评论中写总结并附 PR 链接，且**必须**写入本次 **AI 会话 ID**（agent transcript UUID）与 transcript 路径，便于续修（细则见 `00-common.md`「AI 会话 ID」、`03` Step D）。**不得**在仅本地提交后结束任务（无法推送时须说明原因）。**始终在仓库根主工作树**内编码与提交（细则见 `03`「主工作树」）。
8. **审核 PR 时**：精读 `06-pr-review.md`；若发现 🔴 必须修复问题，先帮用户修复代码并 push，再执行 Approve；无阻塞问题则直接 Approve。
9. **合并 PR 时**：精读 `08-pr-merge.md`；**先**用 `gh pr view --json mergedAt` 判断是否已合并；有冲突则按该文件合并 base、解决后 push，再 `gh pr merge`；合并后根据 `closingIssuesReferences` 校验，对仍 OPEN 的关联 issue 执行 `gh issue close` 并评论说明。

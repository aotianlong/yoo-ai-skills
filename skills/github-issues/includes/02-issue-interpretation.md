[← 技能索引](../SKILL.md)

# Issue 解读（含批量扫描与脚本）

## Issue 解读流程（用户要求解读/分析 issue 时）

当用户说以下任意形式时，进入此流程：
- `"解读这个 issue https://github.com/.../issues/xxx"`
- `"分析 issue #xxx"`
- `"解读 issue"`
- `"帮我看看这个 issue"`
- `"解读一下 #xxx"`（口语，最常见）
- `"解读 #xxx"`
- `"看一下 #xxx"`
- `"分析 #xxx"`
- `"帮我解读 #xxx"`
- `"看看 #xxx"`

### 何为「解读」（与泛泛分析的区别）

**解读**不是只复述现象或列「可能原因」，而是要写出**可以直接照着做的修复方案**，使后续 AI 或开发者能**按评论落地改代码**，减少走弯路。

- **必须包含**：可执行的改动说明（改哪些文件/模块、改什么逻辑或参数、前后端如何配合），以及**如何验证**修复成功。
- **必须检索**：解读前在仓库中查找**是否已有类似的其它 OPEN issue**（避免重复开工、便于合并修复或交叉引用），结论写进解读评论（见 Step R2.5）。
- **解读后更新标签**：发帖成功后按 Step R6 **仅追加**缺失标签；**已有标签一律视为故意设置，禁止移除或替换**（见 [`05-reference.md`](05-reference.md) 打标签规则）。
- **预览用途**：评论发在 issue 上后，**你（或产品）可以在触发「自动修复」之前先读一遍**；若方案不对，可在 issue 里回复纠正，再让 AI 按更新后的共识修复。

**目标**：结合 issue 描述、截图、URL、控制台与网络信息，在代码库中定位依据，在 issue 下发表一条 **`## 🔍 Issue 解读`** 评论，结构以 **「可执行修复方案」** 为核心。

> **仅 OPEN**：若 `gh api .../issues/{n}` 返回的 `state` 为 `closed`，**不要**发布解读评论；仅在对话中给出分析摘要，并说明该 issue 已关闭。

> **子 issue / 父 Epic**：若正文或评论中有子任务编号、父任务引用，先按 [`07-sub-issues.md`](07-sub-issues.md) 做只读汇总；解读**父** issue 时，在 Step R2.5 的关联一节列出 **OPEN 的子 issue**，避免与子任务脱节。

> **防重复解读**：发帖前检查 issue **正文**与**已有评论**是否已含 `## 🔍 Issue 解读`（或同时含「Issue 解读」与「🔍」）。若已有，**跳过**，不重复评论。

> **强制要求**（针对仍打开的 issue）：完成分析后，须先把**拟发布的「Issue 解读」全文**在对话中展示，**经用户确认后**，再通过 `gh issue comment` 写入 GitHub。用户说「直接发」等可跳过在对话中二次确认。不能仅在对话中给摘要却从不发帖（除非用户取消发帖）。

### 解读步骤

**Step R1：获取 Issue 完整内容**

```bash
# 获取 issue 详情（含 body）
gh api repos/aotianlong/container-house/issues/{number}

# 获取 issue 评论
gh api repos/aotianlong/container-house/issues/{number}/comments
```

**Step R2：分析 Issue 内容**

阅读 issue 的标题、描述，重点关注：
- 问题现象描述
- 系统信息（URL、用户、浏览器等）
- 控制台错误信息
- 网络请求错误（特别是 4xx/5xx 响应）
- 截图链接

**Step R2.5：检索是否存在类似的 OPEN issue（必做）**

在写「可执行修复方案」之前，先确认**其它仍打开的 issue**里是否已有**同一根因、同一页面或高度重叠**的记录，避免 AI/多人重复修同一件事。

1. **提炼检索词**：从当前 issue 标题与正文取出 2～4 个关键词（模块如「交易/租赁/协商」、页面路径片段、功能点如 `stage_counts` / `unified-orders` / `gate buy` 等）。
2. **命令行检索**（在仓库根目录或任意目录均可）：

```bash
# 方式 A：GitHub 搜索（推荐，支持多关键词组合试几次）
gh search issues "关键词1 关键词2" --repo aotianlong/container-house --state open --limit 30

# 方式 B：列出近期 OPEN 后人工扫标题（补充漏网之鱼）
gh issue list --repo aotianlong/container-house --state open --limit 150 \
  --json number,title | python3 -c "import sys,json; [print(i['number'], i['title']) for i in json.load(sys.stdin)]"
```

3. **处理规则**：
   - **排除**当前正在解读的 issue 编号。
   - 对候选 **#xxx**：读标题与必要时 `gh api repos/.../issues/xxx` 看 body 前两段，判断是**重复**、**同源不同表象**还是**仅相关**。
   - 若发现重复或强相关：在解读评论的 **「相似 / 关联 OPEN issue」** 一节中列出，并写一句**建议**（例如「与 #155 合并修复」「先修 #155 再验证本 issue 是否仍存在」）；若确认无关则不必罗列。

> 若检索结果为空或仅弱相关，解读评论中仍应明确写一句 **「未发现明显重叠的 OPEN issue」**（或等价表述），表示已做过这一步。

**Step R3：分析截图（如有）**

如果 issue body 或评论中包含图片（`![...](url)` 格式），按以下顺序尝试获取：

**方式 A（优先）：用 playwright-cli 打开并截图**

直接让浏览器访问图片 URL，绕过 HTTP 客户端的限制（如 500 错误、签名过期、重定向等），通常成功率最高：

```bash
playwright-cli open "https://图片URL"
playwright-cli screenshot --filename=/tmp/issue-screenshot.png
playwright-cli close
```

然后用 Read 工具读取 `/tmp/issue-screenshot.png` 进行图片分析。

**方式 B（备用）：curl 直接下载**

如果 playwright-cli 不可用或图片 URL 是简单公开链接，可用 curl：

```bash
IMG_URL="https://..."
curl -L "$IMG_URL" -o /tmp/issue-screenshot.png
```

然后用 Read 工具读取 `/tmp/issue-screenshot.png` 进行图片分析。

**方式 C（最后备用）：WebFetch 直接读取**

若以上均无法访问，尝试用 WebFetch 工具直接抓取 URL（适用于普通 PNG/JPG 公开链接）。

读取到图片后，重点分析：
- 识别截图中标注的问题区域（红色箭头、红色文字、手写批注）
- 识别页面路径（面包屑导航、URL、标签页标题）
- 识别错误提示、异常状态、UI 截断/溢出现象

**Step R4：定位代码根因**

根据分析结果，在代码库中查找相关文件：
- 根据页面 URL 找到对应的 Vue 页面文件
- 根据网络请求错误找到对应的 API 路由
- 根据控制台错误找到相关的前端代码

**Step R5：生成解读评论并发布到 Issue**

> **此步骤为必须执行步骤**（在仍打开且需发帖的前提下），不可跳过。分析完成后，**先**在对话中输出与下述模板一致的**完整评论正文**（`## 🔍 Issue 解读` 起至结尾），**等待用户明确确认**后，再执行 `gh issue comment`。用户已说「直接发」「按这个发」时可省略等待。

在 issue 下方添加评论，格式如下（**「可执行修复方案」为整段评论的重点**，勿用空泛的「优化一下」代替）：

```bash
gh issue comment {ISSUE_NUMBER} --repo aotianlong/container-house --body "$(cat <<'EOF'
## 🔍 Issue 解读

### 问题分析

**现象**：（一句话）

**根本原因**：（说明依据：相关文件/接口/状态机/字段，避免纯猜测）

**影响范围**：（用户或场景）

### 截图分析

（若有截图：标出与缺陷直接相关的 UI/文案/状态）

### 相似 / 关联 OPEN issue

（**必填**。做过 Step R2.5 后的结论。）

- **未发现**与当前问题明显重叠的其它 OPEN issue。（可注一句检索用的关键词。）
- 或 **存在关联**，例如：
  - #155 — 标题摘要 — **关系**：与当前同源 / 重复场景 / 依赖先修复 — **建议**：合并 PR 或修复顺序

### 可执行修复方案（供实现与预览）

> 以下步骤应具体到**能开 PR 的程度**，便于 AI 按此修改；维护者可在自动修复前**预览本段**确认方向是否正确。

**改动清单**（按优先级）：
1. **文件** `path/to/file.ext` — **做什么**：例如「在 X 函数中当 Y 时将查询参数 Z 传入 API」「增加 v-model 与 Tab 的 stage 同步」。
2. **文件** `path/to/other.ext` — **做什么**：…

**关键逻辑 / 伪代码**（可选但推荐）：

```text
# 或简短 TS/Ruby 片段，说明判断分支与数据流
```

**边界与风险**：（兼容旧数据、需不需要迁移、是否影响 Gate buy 等）

### 验证方式

- **手工**：复现步骤 → 修复后期望看到…（含 URL）
- **自动化**：（若适用）建议补哪类 E2E / 单测、断言什么

### 优先级建议

（高/中/低 + 一句理由）
EOF
)"
```

评论发布成功后，将 **issue 链接与解读评论锚点** 告知用户，并说明：**可在发起「请按 issue 修复」类任务前先打开该评论预览方案**。

**Step R6：解读后更新标签（仅追加，不覆盖）**

> **原则**：issue 上**已经存在的标签**视为创建人或团队**故意选择**，解读流程**不得**用「更正」名义删掉或换掉。只补充解读后认为仍有必要、且**当前未挂载**的标签。

1. **查看现有标签**：

```bash
gh issue view {ISSUE_NUMBER} --repo aotianlong/container-house --json labels \
  -q '.labels[].name'
```

2. **根据解读结论**（现象类型、模块、优先级、文案/多语言等）从 [`05-reference.md`](05-reference.md) 的现有标签表中选取**适用项**，排除已存在的名字。

3. **只追加缺失项**（GitHub 对已存在的 label 再次 `--add-label` 一般无害；若你希望幂等可先比对再调用）：

```bash
gh issue edit {ISSUE_NUMBER} --repo aotianlong/container-house --add-label "bug,ui"
```

4. **禁止**在解读流程中使用 `--remove-label` 或任何「整表覆盖」式改标签。

5. **冲突时的保守处理**：若解读认为应是 `bug`，但 issue **已有** `enhancement`（或反之），**不要**追加对立类型；若**已有**任一等级的 `*-priority`，**不要**再追加其它 `*-priority`（避免与现有优先级意图冲突）。可在解读评论末尾用一句说明「标签保持现状，因已有 xxx」。

### 解读与后续自动修复的衔接

当之后进入 **Issue 修复流程** 时，实现方（人或 AI）应 **优先阅读** 该 issue 下 **`## 🔍 Issue 解读`** 中的 **「可执行修复方案」**；若与当前代码已有出入，以 issue 上最新讨论为准。

---

### 批量解读与全仓库扫描（仅 OPEN / 防重复解读）

当用户要求**解析仓库内 issues**、**只解读仍打开的**、且**已解读过的不重复**时：

#### 范围：仅 OPEN

- **不**对 `closed` issue 发解读评论（扫描脚本只拉取 `states: [OPEN]`；批量发帖脚本发帖前会再次校验 `state`）。
- 单条人工解读流程同样适用：closed → 仅对话分析，不发评论。

#### 「已解读」判定（防重复）

满足以下**任一**即视为**已有解读**，**禁止**再发一条解读评论：

- issue **正文**或**任意评论**中出现 **`## 🔍 Issue 解读`**
- 或同时包含 **`Issue 解读`** 与 **`🔍`**（兼容少量历史写法）

#### Step B1：扫描待解读的 OPEN issues（GraphQL）

在**仓库根目录**执行扫描脚本，生成 `tmp/issues-need-interpret.json`：

- `done`：**OPEN** 且已有上述解读标记的编号  
- `need`：**OPEN** 且尚无解读标记的编号（**不含任何 CLOSED**）

```bash
cd "$(git rev-parse --show-toplevel)"
python3 .claude/skills/github-issues/scripts/scan_issue_interpretation_status.py
```

脚本路径：`.skills/github-issues/scripts/scan_issue_interpretation_status.py`  
依赖：`gh` 已登录，且对 `aotianlong/container-house` 有读权限。

#### Step B2：对 `need` 中的 OPEN issue 解读

逐条按上文 Step R1～**R6**（**含 R2.5 相似 OPEN 检索**；**R6 仅追加标签**）发帖前**再次**检查正文与评论是否已有解读标记；或将解读正文加入 Step B3 脚本的 `INTERPRETATIONS` 后执行（脚本内建防重复与 OPEN 校验）。手工批量解读时，每条都要做 **R2.5**，并在评论里写 **「相似 / 关联 OPEN issue」**；发帖后执行 **R6**。

#### Step B3：批量发布预设解读正文（可选）

脚本路径：`.skills/github-issues/scripts/post_open_issue_interpretations.py`

- 内置字典 `INTERPRETATIONS`：issue 编号 → 完整 Markdown（须含 `## 🔍 Issue 解读`）。
- 对每个编号：**仅当** issue 为 **OPEN** 时发帖；若 **正文或任意评论**已有解读标记 → **SKIP**；若已 **CLOSED** → **SKIP**。
- 评论草稿会写入仓库 `tmp/issue-interpret-comments/{number}.md`，便于 diff 与排查。

**执行方式**（必须在仓库根目录）：

运行前在对话中说明**将发帖的 issue 编号列表**与 **1 条样例解读**（或指向 `tmp/issue-interpret-comments/{n}.md` 的摘要），**经用户确认**后再执行下述命令。用户说「直接跑脚本」可跳过。

```bash
cd "$(git rev-parse --show-toplevel)"
python3 .claude/skills/github-issues/scripts/post_open_issue_interpretations.py
```

**维护说明**：新增需批量发帖的 issue 时，编辑该脚本内 `INTERPRETATIONS`，**必须与 Step R5 + R2.5 一致**：含 **「相似 / 关联 OPEN issue」**（发帖前应用 `gh search issues` 等更新该节），并以 **「可执行修复方案」** 为核心（具体文件 + 做什么 + 验证方式）。

#### Step B4：向全部 OPEN 追加「新规范补充」解读（可选）

当需要**在已有旧版解读之上**，按新规范再发一条、且**不覆盖旧评论**时：

- 脚本：`.skills/github-issues/scripts/append_new_spec_interpret_comments.py`
- 评论标题含 **`## 🔍 Issue 解读（新规范补充）`**；若评论中已含「新规范补充」则 **SKIP**（可重复执行）。
- 正文含 **相似 OPEN**、**可执行方案**、**验证**；具体条目在脚本内 `SIMILAR` / `FIX` 字典维护。
- 草稿：`tmp/issue-new-spec-comments/{number}.md`

**先**在对话中说明将影响的 issue 范围并**经用户确认**；可用 `--dry-run` 预览。用户说「直接跑」可跳过。

```bash
cd "$(git rev-parse --show-toplevel)"
python3 .claude/skills/github-issues/scripts/append_new_spec_interpret_comments.py
# 仅预览：加 --dry-run
```


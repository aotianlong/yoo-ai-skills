[← 技能索引](../SKILL.md)

# 读取 Issue 图片与附件

GitHub issue 中的 **`github.com/user-attachments/...`** 图片与附件**未登录会 404**；`WebFetch` 常超时；裸 `curl` 也会失败。**不要**因此判定「读不到图」——按本节顺序执行即可。

## 何时必读

- 解读 issue（`02` Step R3）
- 解决 issue 前通读上下文（`03`）
- 用户要求「读取 issue 图片」「看看 issue 里的截图」
- issue body/评论含 `<img src="...">`、`![...](url)` 或 `[文件名](https://github.com/user-attachments/files/...)`

## 推荐流程（按优先级）

### Step 1：拉取 issue 正文与 URL

```bash
REPO="${REPO:-aotianlong/container-house}"
ISSUE="${ISSUE:-1096}"

gh issue view "$ISSUE" --repo "$REPO" --json title,body,comments \
  --jq '{title, body, comments: [.comments[].body]}'
```

从 `body` / `comments` 提取：

| 类型 | 典型 URL |
|------|----------|
| 图片 | `https://github.com/user-attachments/assets/<uuid>` |
| 附件 | `https://github.com/user-attachments/files/<id>/<name>` |

也可用脚本自动下载（见下文「一键脚本」）。

### Step 2：用 `gh` 令牌下载（**优先**，成功率最高）

```bash
TOKEN="$(gh auth token)"
OUT="/tmp/issue-${ISSUE}-image.png"

curl -sL \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -o "$OUT" \
  "https://github.com/user-attachments/assets/<uuid>"

file "$OUT"    # 应显示 PNG/JPEG/WebP，而非 ASCII text
ls -la "$OUT"  # 体积应远大于几十字节；若仅 ~9B 且内容为 Not Found → 未带 token 或 URL 错误
```

**附件（HTML / xlsx 导出等）同样要带 token：**

```bash
curl -sL \
  -H "Authorization: Bearer ${TOKEN}" \
  -o "/tmp/issue-${ISSUE}-attachment.html" \
  "https://github.com/user-attachments/files/<id>/<filename>"
```

### Step 3：用 Read 工具读图片

对 Step 2 保存的本地文件调用 **Read**（支持 png/jpg/gif/webp）。在对话中归纳：

- 表格/文档类：列名、颜色图例、每行要点
- UI 截图：页面路径、标注区域、异常状态
- 若图为 Excel/WPS 导出的大表：优先再读同 issue 的 **HTML 附件**（结构化文本比 OCR 更完整）

### Step 4：解析 HTML 附件（大表/对照表 issue）

issue 常同时贴 **截图 + HTML 附件**（如 `wallet-notification-triggers.html`）。HTML 往往含完整表格正文：

```bash
# 在附件 HTML 中搜关键行
rg "wallet_topup|需要修改|message_key" "/tmp/issue-${ISSUE}-attachment.html"
```

WPS/Excel 导出的 HTML 可能用背景色标注状态，例如：

| 背景色（近似） | 常见含义（产品标注） |
|----------------|----------------------|
| `#92D050` 绿 | 不需要修改 |
| `#FFFF00` 黄 | 需要修改 |
| `#BFBFBF` 灰 | 需要删掉 |

以附件 HTML 为准交叉核对截图，避免只读图漏字段。

### Step 5：备用方式

仅当 Step 2 失败时再试：

**A. playwright-cli（公开或已登录浏览器会话）**

```bash
playwright-cli open "https://github.com/user-attachments/assets/<uuid>"
playwright-cli screenshot --filename=/tmp/issue-screenshot.png
playwright-cli close
```

**B. WebFetch** — 对 `user-attachments` 通常无效，勿作为首选。

## 一键脚本

本技能目录下的脚本（需已 `gh auth login`）：

```bash
# 全局安装（~/.claude/skills/github-issues 符号链接）
~/.claude/skills/github-issues/scripts/download_issue_attachments.sh 1096

# 或指定仓库
~/.claude/skills/github-issues/scripts/download_issue_attachments.sh --repo owner/repo 1096

# container-house 等项目内副本
.claude/skills/github-issues/scripts/download_issue_attachments.sh 1096
```

输出目录：`/tmp/issue-<编号>-attachments/`，含 `manifest.json` 与下载的文件。随后对图片用 **Read**，对 `.html` 用 **Read** 或 `rg`。

## 失败排查

| 现象 | 处理 |
|------|------|
| 文件 9 字节、`Not Found` | 未加 `Authorization: Bearer $(gh auth token)` |
| `file` 显示 `ASCII text` | 同上，或 URL 拷贝不完整 |
| `gh auth status` 未登录 | 先 `gh auth login` |
| 图可读但字太小/糊 | 查同 issue 是否有 HTML/表格附件；或请用户补文字说明 |
| 评论里的图 | 对 `comments[].body` 同样提取 URL 后走 Step 2 |

## 禁止

- **不要**仅凭 `WebFetch` 或裸 `curl` 失败就告诉用户「图片无法读取」
- **不要**在未读图/附件前猜测需求（解读或修复规划须基于实际内容）
- **不要**把 `user-attachments` URL 当作公开 CDN；**必须**带 `gh` token

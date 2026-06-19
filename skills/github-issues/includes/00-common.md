[← 技能索引](../SKILL.md)

# 环境与前置

## 前置条件

- `gh` CLI 已登录
- 可无密码 SSH 登录 `aotianlong@pig.rocks`
- 项目仓库：`aotianlong/container-house`

## Issue 图片与附件

GitHub issue 中的 `user-attachments` 资源**必须带 `gh` 令牌**才能下载。解读/解决前读图见 [`10-read-issue-attachments.md`](10-read-issue-attachments.md)。

## 环境地址

| 环境 | 前端 | 后端 API |
|------|------|---------|
| 本地开发 | `http://localhost:4333` | `http://localhost:3000` |
| 本地前端 + 远程 API（`pnpm dev:cgk2`） | `http://localhost:4334` | `https://container-house-api.aotianlong.com` |
| 测试服务器 | `https://ch.aotianlong.com` | `https://container-house-api.aotianlong.com` |

**修复和测试优先级**：
1. 优先在本地环境（`localhost:4333`）复现和修复
2. 本地无法复现时，在 `web2` 目录执行 `pnpm dev:cgk2` 启动本地前端（端口 4334），API 走远程，将测试服务器 URL 的域名替换为 `localhost:4334` 进行调试
3. 需要操作数据库或查看服务器日志时，才 SSH 登录 `pig.rocks`

## AI 会话 ID（解决后记入 issue，便于续修）

Issue **解决总结**（`03-issue-fix.md` 的 Step D 及同类「✅ 解决/修复说明」模板）**必须**包含本次 Cursor Agent **会话 ID**（agent transcript UUID），便于你下次新开对话时让 AI 读取同一会话记录继续改。

| 项 | 说明 |
|----|------|
| **ID 形态** | UUID，与 `~/.cursor/projects/<工作区-slug>/agent-transcripts/<uuid>/<uuid>.jsonl` 目录名一致 |
| **写入位置** | 解决评论正文中独立一行 **`AI 会话 ID`**（与 PR / commit 链接同级，不可省略） |
| **获取顺序** | ① 若当前对话上下文已给出 transcript / 会话 UUID → **原样使用**；② 否则在发 issue 评论**之前**于仓库根执行下方命令 |
| **禁止** | 编造 UUID；确实无法解析时写明「未能解析 AI 会话 ID」，并写出 `agent-transcripts` 目录路径供人工核对 |

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
WS_SLUG="$(echo "$REPO_ROOT" | sed 's|^/||; s|/|-|g')"
TRANSCRIPTS="$HOME/.cursor/projects/${WS_SLUG}/agent-transcripts"
# macOS：按 mtime 取最新 transcript（避免 find|xargs 参数过长）
LATEST="$(find "$TRANSCRIPTS" -name '*.jsonl' -type f -print0 2>/dev/null \
  | xargs -0 stat -f '%m %N' 2>/dev/null | sort -t' ' -k1,1rn | head -1 | cut -d' ' -f2-)"
AGENT_SESSION_ID="$(basename "$(dirname "$LATEST")")"
echo "workspace_slug=$WS_SLUG"
echo "agent_session_id=$AGENT_SESSION_ID"
echo "transcript=$TRANSCRIPTS/$AGENT_SESSION_ID/$AGENT_SESSION_ID.jsonl"
```

**续修**：新开 Agent 对话时附上 issue 评论中的 **AI 会话 ID**，并请 AI 阅读对应 `.jsonl` transcript 后再改代码。

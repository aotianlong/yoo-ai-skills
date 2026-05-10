[← 技能索引](../SKILL.md)

# 通过 GitHub CLI 管理 Gist

使用官方 **`gh gist`** 子命令管理 [GitHub Gist](https://gist.github.com/)。**须已** `gh auth login` 且对目标账号有权限。

## 触发说法（示例）

- 「创建一个 gist」「把这段代码发到 gist」「上传成 gist」
- 「列出我的 gist」「看看我有哪些 gist」
- 「打开 / 查看某个 gist」「 gist 内容是什么」
- 「改一下 gist」「给 gist 加个文件 / 删个文件 / 改描述」
- 「删掉 gist」「克隆 gist 到本地」

## 确认规则（与 [`SKILL.md`](../SKILL.md) 总规则对齐）

| 操作 | 默认 |
|------|------|
| `gh gist list`、`gh gist view`（及 `-w` 仅打开网页） | 只读，无需停顿 |
| `gh gist create`、`gh gist edit`、`gh gist rename`、`gh gist clone` | **默认直接执行**；同条回复用一两句说明「公开/secret、描述、路径」即可。**仅在**参数不完整或用户**明确要求先发预览**时再停顿 |
| `gh gist delete` | **须明确目标 gist ID/URL**；默认交互确认。脚本化可用 `--yes`，**仅当用户明确要求删除该 gist 时**使用 |

执行变更时建议在对话中点名：**公开还是 secret**、**描述**、**文件路径**；删除前核对 **gist ID 或 URL**。

## Gist 标识

CLI 接受 **gist ID**（32 位十六进制）或 **完整 URL**，例如：

- `5b0e0062eb8e9654adad7bb1d81cc75f`
- `https://gist.github.com/OWNER/5b0e0062eb8e9654adad7bb1d81cc75f`

## Step G1：列出

```bash
gh gist list              # 默认最近 10 条
gh gist ls -L 50          # 增加条数；ls 与 list 等价
gh gist list --public
gh gist list --secret
gh gist list --filter '正则'              # 匹配描述或文件名等
gh gist list --filter '关键词' --include-content   # 慢，耗 rate limit，慎用
```

## Step G2：查看

```bash
gh gist view <id或URL>
gh gist view <id> -f file.md       # 只看其中一文件
gh gist view <id> --files         # 只列文件名
gh gist view <id> -r             # 原始文本
gh gist view <id> -w             # 浏览器打开
```

不提供 `<id>` 时，`view` / `edit` / `delete` 会从最近条目中**交互选择**（仅适合真人终端）。

## Step G3：创建

- **默认创建为 secret（不公开索引）**；公开需 **`--public`**。
- 别名：`gh gist new` 等同 `gh gist create`。

```bash
gh gist create ./a.py ./b.md -d "描述"
gh gist create --public ./snippet.sh
echo 'hello' | gh gist create -f hello.txt -
cat cool.txt | gh gist create -f cool.txt -
gh gist create -f build.log - < build.log
gh gist create -w ./file.txt                # 创建后打开浏览器
```

## Step G4：编辑

```bash
gh gist edit <id>                                    # 交互选文件，进默认编辑器
gh gist edit <id> --filename a.md                  # 指定文件，进编辑器
gh gist edit <id> --filename a.md ./local-a.md      # 用本地文件覆盖 gist 中该文件
gh gist edit <id> --add new.txt
gh gist edit <id> --remove old.txt
gh gist edit <id> --desc "新描述"
```

## Step G5：重命名文件

```bash
gh gist rename <id或URL> <旧文件名> <新文件名>
```

## Step G6：删除

```bash
gh gist delete <id或URL>      # 交互确认
gh gist delete <id> --yes     # 不提示（仅用户明确要求时）
```

## Step G7：克隆

```bash
gh gist clone <id或URL> [目录名]
gh gist clone <url> my-gist -- --depth 1    # 额外 git clone 参数接在 -- 后
```

## 注意事项

- **Secret gist** 并非私有：知道链接的人仍可访问；敏感内容勿上传。
- 自动化或 CI 中优先用非交互形式（显式传入 id、必要处 `--yes`），并注意 token 权限与 rate limit。
- 子命令细节以本地 **`gh gist <cmd> --help`** 为准。

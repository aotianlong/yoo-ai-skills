[← 技能索引](../SKILL.md)

# 口述需求创建 Issue

## 口述需求创建 Issue 流程

当用户说以下任意形式时，进入此流程：
- `"帮我添加 issue"`
- `"帮我创建一个 issue"`
- `"新建一个 issue"`
- `"添加一个需求"`
- `"提一个 bug"`
- `"帮我记录一个问题"`

**目标**：根据用户口述的需求/问题，整理成结构化的 GitHub Issue 并创建。

### Step V0：计划与确认（必做，除非用户明确豁免）

在运行 `gh issue create` 之前，在对话中展示**将创建的 issue 草案**（标题、标签建议、body 要点），**等待用户确认**后再创建。用户说「直接创建」「发吧」等可跳过。

### Step V1：收集需求信息

认真听取用户描述的需求/问题，提取关键信息：
- **问题/需求是什么**：核心描述
- **涉及的模块/页面**：交易、租赁、钱包、用户中心等
- **问题类型**：bug、新功能（enhancement）、改进（improvement）、UI 问题等
- **优先级**：高/中/低（如果用户未指定，根据内容判断）

如果用户描述不够清晰，**主动追问**以补充：
- 具体在哪个页面？
- 期望的行为是什么？
- 当前的实际表现是什么？
- 是否有复现步骤？

### Step V2：整理 Issue 内容

将用户口述的内容整理为结构化格式：

```markdown
## 问题描述 / 需求描述
（根据用户描述整理的清晰表述）

## 复现步骤（bug 类）/ 功能说明（需求类）
1. 步骤一
2. 步骤二

## 期望行为
（应该是什么样的）

## 实际行为（bug 类）
（目前是什么样的）

## 相关页面
`/path/to/page`
```

### Step V3：发布前检查（默认不停顿）

创建前快速自检：标题（格式：`[模块] 页面 - 问题简述`）、body 完整、标签合理。**默认直接进入 Step V5 创建**。

若用户事先要求「给我看全文再建」，则在对话中展示标题、body、标签并等待；否则不要无故阻断流程。

### Step V4：防重复检查

创建前检查是否已有相似 issue：

```bash
gh issue list --repo aotianlong/container-house --state open --limit 100 \
  --json title,number | python3 -c "
import sys, json
issues = json.load(sys.stdin)
keyword = 'KEYWORD'  # 替换为核心关键词
matches = [i for i in issues if keyword.lower() in i['title'].lower()]
for m in matches:
    print(f'#{m[\"number\"]}: {m[\"title\"]}')
"
```

如果发现相似 issue，告知用户并询问是否仍然创建。

### Step V5：创建 Issue

```bash
gh issue create \
  --repo aotianlong/container-house \
  --title "[模块] 标题" \
  --label "标签1,标签2" \
  --body "$(cat <<'EOF'
（Step V2 整理好的内容）
EOF
)"
```

创建完成后，输出 issue 链接给用户。

### Step V6：追加操作（可选）

创建完成后，询问用户：
- 是否需要继续添加其他 issue？
- 是否需要立即开始解决此 issue？（进入 Issue 解决流程 Step A）


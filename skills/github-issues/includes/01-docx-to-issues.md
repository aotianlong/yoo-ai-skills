[← 技能索引](../SKILL.md)

# 从 Word 文档创建 GitHub Issues

## 完整流程

### Step 0：计划与确认（必做，除非用户明确豁免）

在运行 pandoc/解压/上传/创建 issue 之前，在对话中输出**执行计划**并**等待用户确认**，例如：

- 待处理的 **`.docx` 路径**与文档名、是否已做过 **Step 2 防重复** 的结论（将新建几条 / 是否跳过已有关联 issue）；
- 根据初读或页数/图片量给出的 **预计 issue 条数（区间也可）**、**标签策略**（见 [`05-reference.md`](05-reference.md)）；
- 若已能逐条草拟：**每条建议标题**（`[模块] …` 格式）与类型（bug/enhancement 等）。

用户确认（如「可以，按这个建」）后，再进入 Step 1。用户说「直接建」「免确认」等可跳过本步。

### Step 1：确定文档路径

默认文档目录：`/Users/aotianlong/Documents/container house/`

用户若只说文件名（如"32-交易部分问题.docx"），先在默认目录查找，找不到再在项目根目录查找。

### Step 2：防重复检查

**在创建任何 issue 之前**，先检查是否已存在同名文档的 issues：

```bash
gh issue list --repo aotianlong/container-house --state all --limit 200 \
  --json title,body,number \
  | python3 -c "
import sys, json
issues = json.load(sys.stdin)
doc_name = 'DOCNAME'  # 替换为实际文档文件名
matches = [i for i in issues if doc_name in (i.get('body') or '')]
for m in matches:
    print(f'#{m[\"number\"]}: {m[\"title\"]}')
"
```

如果已有匹配的 issues，询问用户是否继续（跳过已有的，只创建新的）。

### Step 3：提取文档内容

```bash
# 转换为 markdown（检查是否只有图片）
pandoc --track-changes=all "文档路径.docx" -o /tmp/doc-content.md

# 解压提取图片
unzip -o "文档路径.docx" -d /tmp/doc-unpacked/
ls /tmp/doc-unpacked/word/media/
```

### Step 4：分析图片内容

逐张读取图片（使用 Read 工具），识别：
- 红色箭头/标注指向的问题区域
- 红色文字说明的问题描述
- 页面路径（面包屑导航）
- 问题类型（bug / 功能缺失 / 显示错误等）

### Step 5：上传文档到服务器

```bash
# 上传原始 docx 文件
REMOTE_DOC_DIR="aotianlong@pig.rocks:apps/www.pig.rocks/container-house-assets"
DOC_FILENAME=$(python3 -c "import uuid; print(uuid.uuid4().hex[:16])")
DOC_EXT="${原始文件名后缀}"  # 保留原始扩展名
scp "文档路径.docx" "${REMOTE_DOC_DIR}/${DOC_FILENAME}.docx"
DOC_URL="https://www.pig.rocks/container-house-assets/${DOC_FILENAME}.docx"
```

> 如果 SSH 上传失败，则将文档复制到项目的 `docs/tasks/` 目录并 git push，使用 GitHub blob URL。

### Step 6：上传图片到服务器

```bash
REMOTE="aotianlong@pig.rocks:apps/www.pig.rocks/container-house-assets"
BASE_URL="https://www.pig.rocks/container-house-assets"

# 批量上传，文件名使用随机 hex，保留原始扩展名
for IMAGE in /tmp/doc-unpacked/word/media/image*; do
  EXT="${IMAGE##*.}"
  FNAME=$(python3 -c "import uuid; print(uuid.uuid4().hex[:16])").${EXT}
  scp "$IMAGE" "${REMOTE}/${FNAME}"
  echo "$IMAGE -> ${BASE_URL}/${FNAME}"
done
```

### Step 7：整理需求列表

根据图片分析结果，整理每个问题：

| 字段 | 说明 |
|------|------|
| 标题 | `[模块] 页面 - 问题简述`，如 `[交易] 协商列表 - 红点未清除` |
| 描述 | 问题描述、复现步骤、期望行为、实际行为、相关页面 |
| 截图 | 对应的图片 URL |
| 标签 | 从现有标签中选择（见 [`05-reference.md`](05-reference.md)） |

### Step 8：创建 Issues

```bash
gh issue create \
  --repo aotianlong/container-house \
  --title "[模块] 标题" \
  --label "bug,high-priority" \
  --body "$(cat <<'EOF'
## 问题描述
...

## 复现步骤
...

## 期望行为
...

## 实际行为
...

## 相关页面
`/path/to/page`

---
> 来源：[原始文档名](DOC_URL)
EOF
)"
```

### Step 9：添加截图评论

```bash
gh issue comment ISSUE_NUMBER \
  --repo aotianlong/container-house \
  --body "## 截图

![screenshot](IMAGE_URL)

## 来源文档

📄 [文档名](DOC_URL)"
```

### Step 10：生成需求列表 .md 文件

在 `docs/issues/auto-generated/` 目录下生成 `{原始文档名去掉扩展名}-需求列表描述.md`，内容包含所有 issue 的汇总表格和链接。


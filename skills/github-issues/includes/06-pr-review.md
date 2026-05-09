[← 技能索引](../SKILL.md)

# PR 审核流程

## 触发条件

当用户说以下任意形式时，直接进入此流程：
- `"审核 PR #xxx"`
- `"review PR #xxx"`
- `"帮我看看这个 PR"`
- `"approve PR #xxx"`
- `"请 approve #xxx"`

---

## 阶段一：获取 PR 信息

### Step R1：获取 PR 基本信息

```bash
gh pr view {PR_NUMBER} --json title,body,files,commits,author,baseRefName,headRefName,state,labels
```

重点关注：
- `baseRefName`：目标分支（通常应为 `dev`）
- `files`：改动文件列表与增删行数
- `body`：PR 描述是否清晰说明问题、根因、方案

### Step R2：查看具体 diff

```bash
# 查看全量 diff（建议分文件或按模块查看）
git diff {baseRefName}...HEAD --stat
git diff {baseRefName}...HEAD -- path/to/file
```

---

## 阶段二：代码审核要点

### 2.1 功能正确性

- [ ] 改动是否解决了 PR 描述中的问题？
- [ ] 边界条件是否处理（空值、undefined、null）？
- [ ] 是否有遗漏的场景（如多处使用同一组件/逻辑但只改了部分）？

### 2.2 代码质量

- [ ] 是否有重复代码（同样 watch 逻辑复制 N 份）？
- [ ] 新增 import 是否必要（项目有 auto-import 的应避免重复显式导入）？
- [ ] 是否有格式/缩进错误？
- [ ] 是否遗留了调试代码、注释掉的代码、console.log？

### 2.3 向后兼容性

- [ ] 枚举值/接口字段变更是否破坏现有数据？
- [ ] 默认值修改是否影响已有记录？
- [ ] API 变更是否需要同步后端？

### 2.4 安全与性能

- [ ] 前端过滤是否会绕过后端校验？
- [ ] watch 是否可能造成循环触发？
- [ ] 大列表是否存在性能问题（computed 过重、无缓存等）？

### 2.5 测试覆盖

- [ ] 是否有对应的单元测试/E2E 测试更新？
- [ ] PR 描述中的「验证方式」是否合理可执行？

---

## 阶段三：审核结论输出

输出格式：

```
## PR #xxx 审核报告

**标题**：...
**目标分支**：...
**改动文件**：N 个

---

### 整体评价 ✅ / ⚠️ / ❌

（一段话总结）

---

### 发现的问题

#### 🔴 必须修复（阻塞合并）
- 文件：path/to/file:行号
- 问题描述

#### 🟡 建议修复（不阻塞但影响质量）
- 文件：...

#### ℹ️ 可选改进
- ...

---

### 建议处理项汇总

| 优先级 | 文件 | 问题 |
|--------|------|------|
| 🔴 必须 | file | 描述 |
| 🟡 建议 | file | 描述 |

结论：可 Approve / 需修改后再 Approve
```

---

## 阶段四：执行 Approve 或 Request Changes

### 审核通过（无阻塞问题）

```bash
gh pr review {PR_NUMBER} --approve --body "代码审核通过。{可选补充说明}"
```

### 需要修改

```bash
gh pr review {PR_NUMBER} --request-changes --body "$(cat <<'EOF'
## 需要修改

### 必须修复
1. `path/to/file` — 问题描述

### 建议
- ...
EOF
)"
```

### 仅评论（不 approve/reject）

```bash
gh pr review {PR_NUMBER} --comment --body "审核意见..."
```

---

## 注意事项

- **先修复问题再 Approve**：若发现 🔴 必须修复的问题，应先帮用户修复代码，commit 并 push，再 Approve。
- **保留原有逻辑**：审核时发现的改进建议如用户不要求修改，不要擅自修改代码。
- **关联 Issue**：检查 PR body 是否包含 `Closes #xxx` 关联 issue。
- **需要合并 PR**（判断是否已合并、解决冲突、`gh pr merge`、关闭关联 issue）：见 [`08-pr-merge.md`](08-pr-merge.md)。

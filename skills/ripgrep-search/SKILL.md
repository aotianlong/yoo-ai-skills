---
name: ripgrep-search
description: 使用 ripgrep (rg) 和 fd 高效搜索文件内容、文件名和目录。替代 find/grep 命令，速度更快。当需要查找文件、搜索代码内容、定位目录、或用户提到查找/搜索/定位文件时使用此技能。
---

# 使用 ripgrep 高效搜索

**核心原则**：优先使用 `rg` 替代 `grep`，使用 `fd` 替代 `find`。

## 查找文件名/目录

```bash
# 查找目录（替代 find -type d）
fd -t d "migration" /path/to/search

# 查找文件（替代 find -name）
fd -t f "*.java" /path/to/search

# 查找文件（不限类型）
fd "db/migration" /path/to/search

# 仅在当前目录查找
fd "migration"
```

## 搜索文件内容

```bash
# 基本搜索（替代 grep -r）
rg "pattern" /path/to/search

# 搜索特定文件类型
rg "pattern" --type java
rg "pattern" --type ts
rg "pattern" -g "*.vue"

# 只显示匹配的文件路径
rg -l "pattern" /path

# 显示行号和上下文
rg -n -C 3 "pattern" /path

# 大小写不敏感
rg -i "pattern" /path
```

## 常见替换对照

| 旧命令（慢）| 新命令（快）|
|---|---|
| `find /path -name "*.java"` | `fd -t f "*.java" /path` |
| `find /path -type d -name "migration"` | `fd -t d "migration" /path` |
| `grep -r "pattern" /path` | `rg "pattern" /path` |
| `grep -rl "pattern" /path` | `rg -l "pattern" /path` |
| `find /path -name "*.java" \| xargs grep "pattern"` | `rg "pattern" --type java /path` |

## 实用示例

```bash
# 查找 Spring Boot 迁移脚本目录
fd -t d "migration" /path/to/backend

# 查找所有 Controller 文件
fd -t f "Controller.java" /path/to/backend

# 搜索某个类的使用位置
rg "MemberService" --type java /path/to/backend

# 查找包含某注解的文件
rg "@RestController" -l --type java

# 搜索 Vue 文件中的 API 调用
rg "useApi" -g "*.vue" /path/to/frontend
```

## 注意事项

- `fd` 默认忽略 `.gitignore` 中的文件，加 `-u` 参数可包含被忽略的文件
- `rg` 默认忽略隐藏文件和 `.gitignore` 文件，加 `--hidden` 或 `-u` 可搜索
- 两个工具均已预装在用户环境中

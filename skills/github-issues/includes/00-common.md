[← 技能索引](../SKILL.md)

# 环境与前置

## 前置条件

- `gh` CLI 已登录
- 可无密码 SSH 登录 `aotianlong@pig.rocks`
- 项目仓库：`aotianlong/container-house`

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

[← 技能索引](../SKILL.md)

# 标签、防重复与注意事项

## 标签参考（现有标签）

| 标签 | 用途 |
|------|------|
| `bug` | 功能异常 |
| `enhancement` | 新功能/改进 |
| `high-priority` | 高优先级 |
| `medium-priority` | 中优先级 |
| `low-priority` | 低优先级 |
| `ui` | 界面问题 |
| `i18n` | 国际化 |
| `upload` | 文件上传 |
| `location` | 位置相关 |
| `user-experience` | 用户体验 |
| `data-integrity` | 数据完整性 |
| `needs-clarification` | 描述不清晰，需要补充信息 |
| `in-progress` | 正在修复中 |

### 解读后打标签规则（仅追加、不覆盖）

适用：**Issue 解读流程**（Step R6）在发布解读评论之后。

| 规则 | 说明 |
|------|------|
| **已有 = 故意** | issue 上**已存在的**任一标签，均视为当时有意为之；**禁止**在解读流程中 `--remove-label` 或替换为「你认为更对」的标签。 |
| **只追加** | 仅使用 `gh issue edit --add-label`，补充**当前没有**且与解读结论一致的标签（如 `ui`、`i18n`、`data-integrity`、缺失的 `bug`/`enhancement` 等）。 |
| **类型与优先级不打架** | 若已有 `bug`，不要再加 `enhancement`（反之亦然）。若已有任一 `high-priority` / `medium-priority` / `low-priority`，**不要再加**其它优先级标签。 |
| **工作流类标签** | `in-progress`、`needs-clarification` 等若已存在，**不要**在解读时擅自去掉；是否追加由解读结论决定（例如仍缺信息可建议保留或追加 `needs-clarification`，但不要移除对方已打的 `in-progress`）。 |

标签表见上表；新增仓库标签前应先 `gh label list --repo aotianlong/container-house` 确认名称一致。


## 防重复规则

- 检查 issue body 中是否包含文档文件名
- 检查 issue title 是否与待创建的标题高度相似
- 发现重复时，列出已有 issues，询问用户是否跳过或覆盖

## 注意事项

- 图片上传到 `pig.rocks` 后验证 HTTP 200 再继续
- 文档 URL 优先用 `pig.rocks`，失败则用 GitHub blob URL
- issue 标题格式：`[模块] 页面 - 问题简述`（中文）
- 每个 issue 对应文档中的一个独立问题/截图

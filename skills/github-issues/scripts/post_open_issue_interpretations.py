#!/usr/bin/env python3
"""向 GitHub 发布「## 🔍 Issue 解读」评论（仅 **OPEN**；**防重复**）。

解读正文在技能里定义为：**含可落地修复方案**（具体文件 + 改什么 + 如何验证）+ **相似/关联 OPEN issue 检索结论**（`gh search issues` 等），便于维护者在触发 AI 自动解决 issue **前**预览方案并避免重复开工。内置 `INTERPRETATIONS` 应随 SKILL Step R5 / R2.5 迭代。

规则：
- 仅当 issue **state 为 OPEN** 时才发帖；已关闭则 SKIP。
- **防重复**：issue **正文**或**任意评论**已含 `## 🔍 Issue 解读`（或 Issue 解读+🔍）则 SKIP。

本脚本位于 `.skills/github-issues/scripts/`，请在**仓库根目录**执行：
  python3 .skills/github-issues/scripts/post_open_issue_interpretations.py

评论草稿文件写入仓库 `tmp/issue-interpret-comments/`（便于排查）。
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

REPO = "aotianlong/container-house"
MARKER = "## 🔍 Issue 解读"
# 仓库根目录：.skills/github-issues/scripts/ → parents[3] == container-house
REPO_ROOT = Path(__file__).resolve().parents[3]
TMP = REPO_ROOT / "tmp" / "issue-interpret-comments"
TMP.mkdir(parents=True, exist_ok=True)


def has_interpretation_marker(text: str) -> bool:
    if not text:
        return False
    if MARKER in text:
        return True
    return "Issue 解读" in text and "🔍" in text

# issue_number -> full markdown body
INTERPRETATIONS: dict[int, str] = {
    155: """## 🔍 Issue 解读

### 问题分析

**现象**：在「我的交易订单」搜索订单号后，切换各状态 Tab，列表始终显示同一条记录，Tab 对应的 `stage` 过滤未生效。

**根本原因（推断）**：前端在带搜索关键词（或 deal id）时，请求列表 API 可能未把当前 Tab 的 `stage` / 状态参数一并传给 `trading_deals` 列表接口，或 URL 同步（useUrlSync）在搜索模式下覆盖了 stage，导致各 Tab 共用同一份查询结果。

**影响范围**：所有使用订单号/关键字搜索并依赖 Tab 分流的交易用户。

### 相关页面 / 接口

- 页面：`/home/tradings/orders`（文档路径；线上可能对应 unified-orders）
- 列表：`GET /api/v1/trading_deals`（含 `stage`、`page`、`pageSize`、搜索参数等）

### 修复方向

1. 核对订单列表页在「有搜索条件」时是否仍向 API 传入当前 Tab 的 `stage`（及排序字段）。
2. 检查 `useUrlSync` / query 合并逻辑：搜索不应清空 `stage`。
3. 补一条 E2E：搜索固定订单号后切换 Tab，断言请求参数与列表内容随 Tab 变化。

---
*（自动解读，便于排期与修复对齐）*""",
    202: """## 🔍 Issue 解读

### 问题分析

**现象**：买方发布的需求单，由卖方发起/参与协商并成交后，统一订单或协商卡片上仍显示「买家出价」、且买卖双方角色文案与真实身份不一致（「开始协商的人被当成买家」）。

**根本原因（推断）**：UI 侧对「需求单 / 供应单」场景下 `customer` / `merchant` 与「买方 / 卖方」的映射使用了单一默认（例如按发起协商的一方显示为买家），未结合 `offer` 的 `direction`（buy/sell）或挂单类型区分展示。

**影响范围**：需求单（demand）路径下所有参与协商双方。

### 相关页面

- `https://ch.aotianlong.com/tradings/unified-orders` 及关联协商详情。

### 修复方向

1. 以后端实体为准：根据当前用户相对 `Trading`/`Offer` 的 buyer/seller 角色渲染「买方报价 / 卖方报价」等文案，而非仅按「谁先点协商」。
2. 与 #254 同类问题可合并排查（需求单下报价方向展示）。

---
*（自动解读）*""",
    209: """## 🔍 Issue 解读

### 问题分析

**现象**：租赁（或非货款场景）下，发票明细与支付页出现「货款」行项目，但汇总金额仍正确。

**根本原因（推断）**：发票/支付明细模板复用了交易订单的 line item 构建逻辑，对租赁单或未拆分为「货款」的 deal 仍输出了 `goods`/`货款` 类科目；或枚举映射把某项费用错误标成货款。

**影响范围**：租赁支付、发票 PDF/前端明细。

### 修复方向

1. 区分 `TradingDeal` / `LeasingDeal` 的费用项配置，租赁路径排除「货款」行。
2. 核对后端 Entity 与前端展示用的费用类型映射。

---
*（自动解读）*""",
    210: """## 🔍 Issue 解读

### 问题分析

**现象**：任务类通知在任务通知列表中仍为英文（或模板键未本地化），与产品期望中文不一致。

**根本原因（推断）**：通知 `title`/`body` 来自后端固定英文或 i18n key 未在 zh-CN 配置；或 Message Session 模板未走前端 `t()`。

**影响范围**：`notificationType=task` 的通知列表与推送文案。

### 修复方向

1. 后端通知模板按用户 `locale` 返回已翻译文案，或返回 i18n key 由前端翻译。
2. 对照 `web2/locales` 补全任务通知相关键。

---
*（自动解读）*""",
    246: """## 🔍 Issue 解读

### 问题分析

**现象**：「进行中」各子 Tab 数字之和与「全部」Tab 数字之和不一致（例：11+20 ≠ 11+20+12+6 的语义预期），用户怀疑 `stage_counts` 与列表过滤不一致。

**根本原因（推断）**：`trading_deals/stage_counts` 的统计口径（是否含议价中、是否含 gate buy、是否去重取消单）与列表页 `stage=active` 等参数不一致；或前端把「进行中」与「全部」用了不同的默认筛选。

**影响范围**：统一订单页 Tab 徽章与列表。

### 修复方向

1. 对齐 `stage_counts` 与列表 API 的同一套查询 scope。
2. 文档化各 stage 定义，避免「议价中」同时计入多个分类。

---
*（自动解读）*""",
    248: """## 🔍 Issue 解读

### 截图分析

截图页面为「发布采购需求」表单。**交货方式**一组单选项旁的中文文案存在明显错别字/乱字（识别为类似「坏地交」），应与产品文案一致为 **Pick-up / Gate-buy** 对应的中文（例如「提货 / 到库」或你们已定稿的「本地交」类表述）。用户反馈「看图片中文字」即指此处文案需修正。

### 问题分析

**现象**：发布需求页关键选项中文展示错误，影响理解。

**根本原因（推断）**：`web2` 中该表单项的 i18n 字符串录入错误或键复用导致显示异常。

### 相关页面

- `/tradings/demand-new`

### 修复方向

修正对应 `locales/zh-CN`（及 en）中交货方式选项翻译，并全站检索是否还有相同错误键。

---
*（自动解读）*""",
    249: """## 🔍 Issue 解读

### 问题分析

**现象**：上传提箱单（pick up notice）表单中，免费天数、数量未自动带出协商约定值，仍显示未填或默认空。

**根本原因（推断）**：`pick_up_notices?dealId=...&mode=form` 返回的默认值未从 `negotiation`/`deal` 的最终条件填充；或前端未将 API 默认值写入只读字段（与 #154/#153 同类）。

**影响范围**：交易提箱通知发布流程。

### 修复方向

1. 后端 form 接口返回 `freeDays`、`quantity` 等与协商一致。
2. 前端表单 `initialValues` 使用接口默认值并只读展示。

---
*（自动解读）*""",
    251: """## 🔍 Issue 解读

### 问题分析

**现象**：在「进行中的订单」列表中出现「议价中」状态的记录，用户不理解为何已进入订单列表仍显示议价中。

**根本原因（推断）**：统一订单的 `stage` 划分把「已生成订单但仍在议价/改价流程」或「订单与协商状态未完全闭环」算入 active；或列表混入了 `TradingNegotiation` 维度的状态。

**影响范围**：租赁/交易统一订单「进行中」列表（issue 上下文为 `leasings/unified-orders`）。

### 修复方向

1. 明确产品规则：何种 negotiation 状态应对应订单列表哪一列。
2. 调整 API 过滤或前端展示标签，避免与「我的协商」重复混淆。

---
*（自动解读）*""",
    252: """## 🔍 Issue 解读

### 问题分析

**现象**：当类别选择「罐箱」时，箱型下拉仍为干货箱选项，未展示罐箱专用箱型列表。

**根本原因（推断）**：箱型枚举/下拉数据源未按 `category`（dry/tank 等）切换，全站共用 dry 列表。

**影响范围**：所有依赖箱型下拉的表单与筛选器。

### 修复方向

1. 在 `useEnum` 或静态配置中按 category 切换 tank 箱型集合（issue 正文已列明罐箱型号清单，可作为配置基准）。
2. 回归测试交易/租赁发布与搜索页。

---
*（自动解读）*""",
    253: """## 🔍 Issue 解读

### 问题分析

**现象**：交易已完成仍出现在「进行中」订单 Tab。

**根本原因（推断）**：`trading_deals` 的 `stage` 或 completed 标志未在终态（如 completed/cancelled）及时更新；或前端「进行中」查询条件过宽未排除已完成。

**影响范围**：统一订单列表分类。

### 修复方向

1. 核对订单完成时后端是否将 deal `stage` 更新为非 active。
2. 对齐 `stage_counts` 与列表过滤。

---
*（自动解读）*""",
    254: """## 🔍 Issue 解读

### 问题分析

**现象**：需求单场景下，对方（卖方）报价 2888，己方界面却显示「买方报价 2000」等颠倒。

**根本原因（推断）**：与 #202 同类：列表卡片上「买方/卖方报价」未按 offer 方向与当前用户角色计算，误用了 proposal 的提交者或固定标签。

**影响范围**：协商列表、统一订单卡片（`home/negotiations/trade`）。

### 修复方向

统一封装「当前用户视角下的对方报价 / 己方报价」计算逻辑，并在需求单与供应单上复用。

---
*（自动解读）*""",
    255: """## 🔍 Issue 解读

### 问题分析

**现象**：交易协商列表排序不是「最近有操作/状态变更」优先，用户难以看到最新活跃协商。

**根本原因（推断）**：API 使用 `orderBy=createdAt` 仅按创建时间；未使用 `updated_at` / `last_message_at` 等字段。

**影响范围**：`/home/negotiations/trade` 列表。

### 修复方向

1. 后端支持按 `updated_at` 或业务「最后事件时间」排序。
2. 前端默认改为最近活动优先。

---
*（自动解读）*""",
    256: """## 🔍 Issue 解读

### 问题分析

**现象**：协商进行中时，列表展示的 ID 为挂单号，期望展示交易订单号（deal id）。

**根本原因（推断）**：UI 绑定了 `offer.unique_number` 或 `trading_id`，而在未生成 deal 或用户语义中更希望看到 `trading_deal` 的订单号。

**影响范围**：协商列表主键展示。

### 修复方向

产品确认展示规则：无订单时是否显示协商 id；有订单后统一显示 `deal` 编号。前后端字段暴露一致。

---
*（自动解读）*""",
    257: """## 🔍 Issue 解读

### 问题分析

**现象**：用户准备支付时提示账单/支付单已过期，期望将有效期改为约 3 天等更长窗口。

**根本原因（推断）**：支付意图或 wallet 订单过期时间与业务预期不符（当前过短或从创建时刻算未排除节假日）。

**影响范围**：钱包支付、订单支付链接。

### 修复方向

1. 配置化支付过期时间（如 72 小时）并前后端一致。
2. 过期后生成新支付单的引导文案。

---
*（自动解读）*""",
    258: """## 🔍 Issue 解读

### 问题分析

**现象**：平台服务费从原设计 1.35% 调整为 1.5%。

**性质**：**业务规则 / 配置变更**，非 bug。

### 修复方向

1. 更新费率配置（后端计费、展示文案、合同/帮助页）。
2. 全站搜索「1.35」与「1.5」相关展示与公式。

---
*（自动解读）*""",
    259: """## 🔍 Issue 解读

### 问题分析

**现象**：租赁单平台费同样为 1.5%，且由付款方承担。

**性质**：**业务规则确认与实现**，需与交易侧费率逻辑对齐。

### 修复方向

租赁计费模块与发票行项目与 #258 一并调整，明确 payer。

---
*（自动解读）*""",
    260: """## 🔍 Issue 解读

### 问题分析

**现象**：Gate buy 供应挂单下，对方无法发起/进入协商。

**根本原因（推断）**：`negotiations/check_active` 或 start negotiation 流程对 `gate_buy` / 特殊 delivery 模式做了限制；或前端隐藏了入口。

**影响范围**：Gate buy 供应方与需求方。

### 修复方向

1. 查 `check_active` 与 `StartNegotiation` 服务对 gate buy 的分支。
2. 确认产品是否允许 gate buy 议价，若允许则放开 API/UI 限制。

---
*（自动解读）*""",
    263: """## 🔍 Issue 解读

### 问题分析

**现象**：Gate buy 交易订单流程步骤条缺环节、步骤图标/文案标识与普通交易不一致。

**根本原因（推断）**：`gate_buy` 模式在 `trading_deal` 步骤配置（todos/steps）中未完整定义或与 UI 映射表不一致。

**影响范围**：Gate buy 订单详情页进度（例：`unified-orders/1348150`）。

### 修复方向

对齐 Gate buy 与标准交易的阶段机配置及 i18n。

---
*（自动解读）*""",
    264: """## 🔍 Issue 解读

### 问题分析

**现象**：租赁订单流程步骤需要增加一个阶段（具体以截图为准）。

**性质**：**产品流程变更**，依赖截图中的目标步骤结构。

### 修复方向

在后端 leasing deal 状态机与前端步骤条配置中新增阶段，并补测试。

---
*（自动解读）*""",
    265: """## 🔍 Issue 解读

### 问题分析

**现象**：Gate buy 订单流程图第 3、4 步需按设计稿调整（与 #263 相关）。

**性质**：UI/流程与业务对齐。

### 修复方向

与 #263、#266 合并，用同一份 Gate buy 流程定义驱动步骤条与文案。

---
*（自动解读）*""",
    266: """## 🔍 Issue 解读

### 问题分析

**现象**：交易订单详情页步骤条与下方说明文案不对应，需「步骤对应下面的内容」。

**性质**：步骤条标签与详细说明区域内容同步修正。

### 修复方向

核对 `trading_deal` 各 stage 的说明组件与步骤索引。

---
*（自动解读）*""",
    267: """## 🔍 Issue 解读

### 问题分析

**现象**：租赁订单/详情流程步骤应与设计稿（截图）一致。

**性质**：同 #264，租赁侧步骤与文案对齐。

### 修复方向

租赁订单页步骤组件与后端 `leasing_deal` 状态映射统一调整。

---
*（自动解读）*""",
    269: """## 🔍 Issue 解读

### 问题分析

**现象**：租赁协商列表缺少与交易侧类似的「已关闭」分组或筛选，用户无法查看已关闭租赁协商。

**根本原因（推断）**：`negotiations` 列表仅请求 `activeStatus=active`，未提供 closed 或 all。

**影响范围**：`/home/negotiations/lease`

### 修复方向

1. 增加 Tab 或筛选：进行中 / 已关闭（与交易协商一致）。
2. API 支持 `activeStatus` 多值或 `closed` 过滤。

---
*（自动解读）*""",
    270: """## 🔍 Issue 解读

### 问题分析

**现象**：挂单延期/有效期选项中同时出现 14 天与 15 天，业务要求统一为 **仅 14 天**，且延期上限 14 天。

**性质**：配置与文案统一，移除 15 天选项。

### 修复方向

1. 前端选项数组与后端 `extend` 校验上限改为 14。
2. 数据迁移：已有 15 天展示按产品规则是否兜底。

---
*（自动解读）*""",
    271: """## 🔍 Issue 解读

### 问题分析

**现象**：有效期/延期选择器应只保留 3 个选项，**去掉 15 天**（与 #270 配套）。

**性质**：UI 选项裁剪 + 后端允许值对齐。

### 修复方向

与 #270 同一 PR 处理 leasing 供应有效期与 extend API。

---
*（自动解读）*""",
}


def should_skip_issue(number: int) -> tuple[bool, str]:
    """若应跳过发帖，返回 (True, 原因)；否则 (False, '')。"""
    ir = subprocess.run(
        ["gh", "api", f"repos/{REPO}/issues/{number}"],
        capture_output=True,
        text=True,
    )
    if ir.returncode != 0:
        return True, f"无法拉取 issue: {ir.stderr or ir.stdout}"
    issue = json.loads(ir.stdout)
    state = (issue.get("state") or "").upper()
    if state != "OPEN":
        return True, f"非 OPEN（当前 {state!r}）"
    if has_interpretation_marker(issue.get("body") or ""):
        return True, "正文已有解读标记"
    cr = subprocess.run(
        ["gh", "api", f"repos/{REPO}/issues/{number}/comments?per_page=100"],
        capture_output=True,
        text=True,
    )
    if cr.returncode != 0:
        return True, f"无法拉取评论: {cr.stderr or cr.stdout}"
    for c in json.loads(cr.stdout or "[]"):
        if has_interpretation_marker(c.get("body") or ""):
            return True, "评论已有解读标记"
    return False, ""


def post_comment(number: int, body: str) -> bool:
    path = TMP / f"{number}.md"
    path.write_text(body, encoding="utf-8")
    r = subprocess.run(
        [
            "gh",
            "issue",
            "comment",
            str(number),
            "--repo",
            REPO,
            "--body-file",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(f"FAIL #{number}: {r.stderr}")
        return False
    print(f"OK #{number}")
    return True


def main() -> None:
    nums = sorted(INTERPRETATIONS.keys())
    for n in nums:
        skip, reason = should_skip_issue(n)
        if skip:
            print(f"SKIP #{n} ({reason})")
            continue
        body = INTERPRETATIONS[n]
        if MARKER not in body:
            body = MARKER + "\n\n" + body
        post_comment(n, body)
        time.sleep(1.2)


if __name__ == "__main__":
    main()

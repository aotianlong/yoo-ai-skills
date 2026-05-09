#!/usr/bin/env python3
"""为所有 OPEN issue 追加一条「新规范补充」解读评论（可重复执行：已发过则跳过）。

标题固定含「新规范补充」，与旧版「## 🔍 Issue 解读」并存；不修改全局防重复脚本的 MARKER。

用法（仓库根目录）：
  python3 .skills/github-issues/scripts/append_new_spec_interpret_comments.py
  python3 .skills/github-issues/scripts/append_new_spec_interpret_comments.py --dry-run

解读发帖后请按技能 **Step R6** 人工 `gh issue edit --add-label` 补标签；**勿移除已有标签**。本脚本不自动改标签。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

REPO = "aotianlong/container-house"
ID_TAG = "新规范补充"  # 幂等：评论 body 含此串则跳过
REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "tmp" / "issue-new-spec-comments"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def gh_json(*args: str) -> dict | list:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr or r.stdout)
    if not r.stdout.strip():
        return {}
    return json.loads(r.stdout)


def list_open_numbers() -> list[int]:
    data = gh_json(
        "issue",
        "list",
        "--repo",
        REPO,
        "--state",
        "open",
        "--limit",
        "200",
        "--json",
        "number",
    )
    return sorted(x["number"] for x in data)


def already_has_new_spec(number: int) -> bool:
    r = subprocess.run(
        ["gh", "api", f"repos/{REPO}/issues/{number}/comments?per_page=100"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return False
    for c in json.loads(r.stdout or "[]"):
        body = c.get("body") or ""
        if ID_TAG in body:
            return True
    return False


def post_comment(number: int, body: str, dry_run: bool) -> None:
    path = OUT_DIR / f"{number}.md"
    path.write_text(body, encoding="utf-8")
    if dry_run:
        print(f"[dry-run] would post #{number} ({len(body)} chars) -> {path}")
        return
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
        return
    print(f"OK #{number}")
    time.sleep(1.0)


def build_body(
    number: int,
    similar: str,
    analysis: str,
    fix: str,
    verify: str,
) -> str:
    return f"""## 🔍 Issue 解读（{ID_TAG}）

> 与历史「Issue 解读」评论可同时保留。本节按 `.skills/github-issues/includes/02-issue-interpretation.md`：**相似 OPEN**、**可执行修复方案**、**验证**。

### 相似 / 关联 OPEN issue

{similar}

### 问题分析

{analysis}

### 可执行修复方案

{fix}

### 验证方式

{verify}
"""


# 手工维护：同类 OPEN 交叉引用（发帖前已对照当前 open 列表）
SIMILAR = {
    155: "- #246、#253：统一订单列表 Tab/阶段与展示口径相关，可一并回归。\n- 未发现与本 issue 完全重复的其它 OPEN。",
    202: "- **#254**：同为需求单场景下买卖方/报价文案颠倒，建议同一 PR 修根因。\n- 修复后两条 issue 一起验收。",
    209: "- 租赁侧费用展示可与 **#258/#259**（费率）变更同一轮测试；无其它完全重复 OPEN。",
    210: "- 与通知/i18n 相关的还有任务类文案 scattered；无同标题重复 OPEN。",
    246: "- **#253**：均涉及「进行中 / 已完成」与列表阶段划分。\n- **#155**：Tab 与列表查询参数一致性。",
    248: "- 与 **#249** 同属交易发布/表单文案与默认值问题，可同页面回归。\n- 无其它完全重复 OPEN。",
    249: "- **#248**：发布需求/表单；与提箱单默认值类 **#154/#153**（若仍有关闭单可参考）不同但可共用 pick_up_notices 逻辑排查。",
    251: "- **#253**：订单列表出现议价态；与租赁 **#264/#267**（阶段展示）不同模块但可对照阶段定义。\n- 无完全重复 OPEN。",
    252: "- 全站箱型枚举类需求；无同主题重复 OPEN。",
    253: "- **#246**、**#251**：统一订单阶段与计数。\n- **#155**：列表过滤。",
    254: "- **#202**：同一根因（需求单角色与报价展示）。建议合并修复。",
    255: "- 与 **#256**（协商列表展示）同属 `home/negotiations/trade` 列表体验；可同一 PR 调排序与展示字段。",
    256: "- **#255**：协商列表；展示 ID 与排序可一起验收。",
    257: "- 支付单/账单过期与钱包流程相关；无同句重复 OPEN。",
    258: "- **#259**：租赁费率与交易费率需同一轮配置与文案替换；建议同一 PR。",
    259: "- **#258**：同上。",
    260: "- **#263/#265/#266**：Gate buy 流程与入口；可一起排查 `check_active` 与交易模式分支。",
    263: "- **#265**、**#266**：Gate buy 步骤条与文案；**#260**：无法协商入口。\n- 建议合并为「Gate buy 交易闭环」一次修复。",
    264: "- **#267**：租赁步骤与流程图；与交易 Gate buy 组不同但可对照步骤组件实现。",
    265: "- **#263**、**#266**、**#260**：Gate buy 一组。",
    266: "- **#263**、**#265**、**#260**：Gate buy 一组。",
    267: "- **#264**：租赁步骤；可与租赁详情页 step 配置同查。",
    269: "- 交易侧协商「已关闭」若已实现，可对齐租赁 **#269** 同一套 API 参数；无其它重复 OPEN。",
    270: "- **#271**：租赁挂单有效期/延期天数选项；应同一 PR 收敛 14 天与选项个数。",
    271: "- **#270**：同上。",
}

FIX = {
    155: """1. **根因已定位**：前端 `web2/src/composables/useUnifiedOrderList.ts` 在存在 `searchKeyword` 时不传 `stage`；后端 `app/api/container_house/api/trading_deal.rb` GET 在 `k.present?` 时同样不应用 `by_unified_stage`（约 279–281 行）。
2. **后端**：改为在 `k` 与 `stage` 同时存在时**先** `keyword_search(k)` **再** `by_unified_stage(stage)`（或等价交集），并补接口测试。
3. **前端**：去掉「有关键字就不传 stage」分支，始终传当前 Tab 的 `stage`（非 `all` 时）。
4. **回归**：`useUnifiedOrderStageCounts` 与列表在搜索态下是否仍需对齐，视产品口径调整 `stage_counts` 请求参数。""",
    202: """1. **定位**：`tradings/unified-orders` 列表卡片、`TradingNegotiation` 卡片上「买方/卖方报价」文案与 `priceLabel` 计算（检索 `useUnifiedOrderPrice`、`useUnifiedOrderStatusCard`、negotiation 相关组件）。
2. **规则**：以 `Trading`/`Offer` 的 buy/sell 方向 + 当前用户相对 offer 的角色为准，**禁止**仅用「谁先发起协商」推断买家。
3. **对齐**：与 #254 共用一套「当前用户视角的对方报价」函数，并在需求单（demand）分支单测或 Storybook 快照。""",
    209: """1. **定位**：租赁支付页、发票/PDF 行项目构建（后端 Entity + 前端钱包/订单支付明细）；检索 `货款`、`goods`、leasing invoice。
2. **改动**：`LeasingDeal` 路径下移除或映射掉「货款」科目，仅保留租赁约定费用项；与交易 `TradingDeal` 模板分离。
3. **对齐**：总额以现有正确总金额为基准，防止拆行后 double-count。""",
    210: """1. **定位**：`notificationType=task` 的 title/body 生成（后端模板或前端 `t()`）；对照 `web2/locales/zh-CN` 与消息模板。
2. **改动**：任务通知走 zh-CN 文案或返回 i18n key；避免硬编码英文。""",
    246: """1. **定位**：`useUnifiedOrderStageCounts`（`web2/src/composables/useUnifiedOrderStageCounts.ts`）与 `GET /trading_deals/stage_counts` 的筛选参数是否**与列表 `loadData` 完全一致**（时间、角色、搜索词等）。
2. **后端**：`trading_deal.rb` stage_counts 与列表 endpoint 共用同一套 scope 构建函数，避免两套口径。
3. **文档化**：各 Tab 数字含义与「全部」关系写进注释或 docs。""",
    248: """1. **定位**：`web2` 发布采购需求页 `tradings/demand-new`（或等价路由）交货方式 Radio 的 i18n。
2. **改动**：修正「提货 / Gate-buy」对应中文（当前错字如「坏地交」类）；查 `rg` 同一 key 是否复用在别处。""",
    249: """1. **定位**：`GET /pick_up_notices?dealId=&mode=form` 默认值与前端表单 `initialValues`（`pick_up_notice` 相关页）。
2. **改动**：后端返回协商确定的 `freeDays`、数量；前端只读展示并提交校验与之一致。""",
    251: """1. **产品确认**：「进行中的订单」列表是否应包含 `negotiating` 或仅 deal 执行态。
2. **实现**：调整 `leasing_deals`/`trading_deals` 列表 `stage` 过滤或前端 Tab 映射；与 #253 统一口径。""",
    252: """1. **定位**：`useEnum` 或箱型静态表；所有 `category=tank`（或罐箱）时的下拉数据源。
2. **改动**：增加 issue 正文中列出的罐箱型号集合；交易/租赁发布、筛选、Banner 全站切换。""",
    253: """1. **定位**：deal 完成时 `simplifiedStage`/后端状态与 `by_unified_stage('active')` 是否仍命中；`web2` Tab 过滤。
2. **改动**：终态写入后确保不再出现在 active；必要时修正 `by_unified_stage` scope。""",
    254: """1. 与 **#202** 同一修复：需求单下报价标签与 `priceLabel` 角色映射。""",
    255: """1. **后端**：`GET /negotiations` 支持按 `updated_at` 或最后消息时间排序；或新增 `orderBy=lastActivityAt`。
2. **前端**：`home/negotiations/trade` 列表默认使用新排序参数。""",
    256: """1. **产品**：无 deal 时显示协商 ID 还是挂单号；有 deal 后显示 `deal.orderNo`。
2. **前端**：协商列表卡片主标题字段改为上述规则；避免长期显示 `offerId` 造成与订单号混淆。""",
    257: """1. **定位**：钱包支付意图、`Order`/`WalletTransaction` 过期字段与配置（Rails model / service）。
2. **改动**：将有效支付窗口改为可配置（如 72h），前后端展示一致；过期后一键重新生成支付单入口。""",
    258: """1. **定位**：全站 `1.35`、`1.35%` 与计费公式（Rails service + 前端展示）。
2. **改动**：改为 **1.5%**；与 **#259** 同一提交。""",
    259: """1. 与 **#258** 同步；租赁侧明确「付款方付平台费」的扣费点与发票行项目。""",
    260: """1. **定位**：`negotiations/check_active`、`StartNegotiation`、Gate buy 供应的 `trading` 类型分支（Ruby service + Grape）。
2. **改动**：若产品允许 Gate buy 发起协商，移除错误限制；否则产品确认后改文案关闭入口。""",
    263: """1. **定位**：`gate_buy` 下 `TradingDeal` 步骤条数据源（todos / `useUnifiedOrderProgress` 映射）。
2. **改动**：与标准交易对齐缺失环节与图标；参考设计稿（issue 截图）。""",
    264: """1. **定位**：租赁订单详情步骤配置（前后端 stage 枚举与 i18n）。
2. **改动**：按截图增加阶段并更新状态机跳转。""",
    265: """1. 与 **#263/#266** 共用 Gate buy 步骤配置与 i18n。""",
    266: """1. **定位**：交易订单详情步骤与下方说明组件索引对齐（`tradings/unified-orders/[id]`）。
2. **改动**：修正 step 与文案数组一一对应。""",
    267: """1. 与 **#264** 类似：租赁详情步骤条与说明；复用租赁 stage 配置单一数据源。""",
    269: """1. **定位**：`home/negotiations/lease` 列表 API `activeStatus`；对比交易协商「已关闭」Tab。
2. **改动**：增加 closed 或 all 筛选；API 与交易侧对齐。""",
    270: """1. **定位**：租赁挂单延期/有效期前端选项与 `PUT .../extend` 校验（`home/leasings`）。
2. **改动**：去掉 15 天选项，上限 14 天；与 **#271** 同一 PR。""",
    271: """1. **定位**：同上；选项只保留 3 档且不含 15 天。
2. **改动**：与 **#270** 同步后端允许值。""",
}

VERIFY = """- 按 issue 描述复现 → 修复后现象消失。
- 相关页面手动走一遍；必要时补 E2E（列表 Tab + 搜索同时存在场景）。"""


def analysis_for(n: int, title: str) -> str:
    return f"**现象**：见 issue 标题与正文。\n**范围**：OPEN #{n} — {title}\n**说明**：本补充聚焦可改代码路径与依赖 issue；细节以仓库代码为准。"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    open_nums = list_open_numbers()
    print(f"OPEN issues: {len(open_nums)} -> {open_nums}")

    for n in open_nums:
        if already_has_new_spec(n):
            print(f"SKIP #{n} (已有{ID_TAG})")
            continue
        title = ""
        try:
            issue = gh_json("api", f"repos/{REPO}/issues/{n}")
            title = issue.get("title") or ""
        except Exception as e:
            print(f"WARN #{n} fetch title: {e}")

        body = build_body(
            n,
            SIMILAR.get(n, f"- 已对照当前 OPEN 列表；请用 `gh search issues` 以标题关键词复查。\n- 本 issue 编号 #{n}。"),
            analysis_for(n, title),
            FIX.get(
                n,
                "1. 根据标题在 `web2/src` / `app/` 下 `rg` 关键词定位页面与 API。\n2. 按产品确认写出最小改动 PR；若信息不足先评论澄清再改代码。",
            ),
            VERIFY,
        )
        post_comment(n, body, args.dry_run)


if __name__ == "__main__":
    main()

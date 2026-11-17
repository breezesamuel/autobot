#!/usr/bin/env python3
"""Collection Skill — 收款自动化全流程
参考: Stripe Payment Links + Alipay native payment flow
"""
from __future__ import annotations
import json
import logging
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger("autobot.collection")


BASE_URL = "https://tools-cn.highkingflower.com"
TIER_PRICES = {"proY": 500, "team": 299, "pro3": 150, "pro": 60, "trial": 1}


def build_pay_link(ref: str, plan: str) -> str:
    return f"{BASE_URL}/api/pay?plan={plan}&slug=tool&ref={ref}"


# ── 消息模板（多版本适配不同客户场景）─────────────────────────────────────────
TEMPLATES = {
    # 合并版：同一客户的多个订单汇总（最高效，推荐）
    "summary_combined": """【{brand}·订单确认提醒】您的账户有待确认订单，共计 ¥{total}：
{order_lines}
⏰ 限时优惠：本周内完成支付，额外赠送3份专业回测报告(C3)。
💳 支付宝直连：{link}""",

    # 单条独立版（适合首次触达或分开发送）
    "single_order": """【{brand}·支付提醒】您的订单 {oid} 已开通。
付款链接: {link}
金额: ¥{amt}
注意: 回测是历史数据，不代表未来收益；非投资建议，风险自负。""",

    # 对公打款专用
    "corporate_remittance": """【{brand}·年费¥{amt} 对公打款】
订单号: {oid}
金额: ¥{amt}
汇款备注: {brand}年付-{oid}-{ref}
收款账户：以正式对公函为准（见运营附件）。
汇款后请回我确认，以便及时开通年费权益。""",

    # Trial到期挽回
    "trial_winback": """您的 {days} 天体验已结束。解锁全部工具 + 专业回测报告(C3) + 行情数据订阅，
专业月度 ¥60/31天，限时新用户 9 折。专属升级链接: {link}""",

    # 续订提醒
    "renewal_reminder": """您的订阅即将到期。续费享 9 折优惠：{link}
（¥{amt}/周期，解锁全部工具 + API + 数据导出 + 优先支持）""",
}

BRAND = "丙大山"


def render_template(key: str, **ctx) -> str:
    tpl = TEMPLATES[key]
    ctx.setdefault("brand", BRAND)
    return tpl.format(**ctx)


# ── 数据解析 ───────────────────────────────────────────────────────────────────
def parse_manual_pending(tsv_path: str | Path) -> list[dict]:
    """解析 manual_pending.tsv → 结构化订单列表"""
    p = Path(tsv_path)
    if not p.exists():
        return []
    rows = []
    with open(p, encoding="utf-8") as f:
        header = f.readline().strip().split("\t")
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= len(header):
                row = dict(zip(header, parts))
                amt = float(row.get("amount", 0) or 0)
                visitor = row.get("visitor", "")
                ref = visitor.split(":")[-1] if ":" in visitor else row.get("id", "")
                rows.append({
                    "source": "manual_8",
                    "order_id": row.get("id", ""),
                    "ref": ref,
                    "amount": amt,
                    "plan": row.get("plan", "m"),
                    "kind": "manual",
                    "ip": visitor.split(":")[0].replace("ip:", "") if ":" in visitor else "",
                })
    return rows


def parse_corporate_orders(json_path: str | Path) -> list[dict]:
    """解析 corporate_899.json → 对公打款订单"""
    p = Path(json_path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
        items = data if isinstance(data, list) else data.get("orders", data.get("items", []))
        return [{
            "source": "corporate_899",
            "order_id": r.get("order_id", ""),
            "ref": r.get("ref", ""),
            "amount": float(r.get("corporate_amount", r.get("amount", 899))),
            "plan": "y",
            "kind": "corp",
            "memo": r.get("remit_memo", f"丙大山年付-{r.get('order_id','')}-{r.get('ref','')}"),
        } for r in items if isinstance(r, dict)]
    except Exception:
        return []


def parse_trial_winback(tsv_path: str | Path) -> list[dict]:
    """解析 trial_winback.tsv → 试用到期用户"""
    p = Path(tsv_path)
    if not p.exists():
        return []
    rows = []
    with open(p, encoding="utf-8") as f:
        header = f.readline().strip().split("\t")
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                row = dict(zip(header, parts))
                rows.append({
                    "source": "trial_winback",
                    "ref": row.get("ref", ""),
                    "amount": 60.0,
                    "plan": "pro",
                    "kind": "trial",
                    "days_ago": float(row.get("距今天", 0) or 0),
                })
    return rows


def scan_all_pending(billing_dir: str | Path = "/opt/bingdashan/data/billing") -> list[dict]:
    """扫描所有待收款订单，按 ref 聚合 + 按金额排序"""
    bd = Path(billing_dir)
    all_orders = []
    all_orders.extend(parse_manual_pending(bd / "manual_pending.tsv"))
    all_orders.extend(parse_corporate_orders(bd / "corporate_899.json"))
    all_orders.extend(parse_trial_winback(bd / "trial_winback.tsv"))

    # 按 ref 聚合（同一客户的多个订单合并）
    grouped: dict[str, list[dict]] = {}
    for o in all_orders:
        grouped.setdefault(o["ref"], []).append(o)

    aggregated = []
    for ref, orders in grouped.items():
        total = sum(o["amount"] for o in orders)
        plans = list({o["plan"] for o in orders})
        kind = "combined" if len(orders) > 1 else orders[0]["kind"]
        aggregated.append({
            "ref": ref,
            "total_amount": total,
            "order_count": len(orders),
            "plans": plans,
            "kind": kind,
            "orders": orders,
            "pay_link": build_pay_link(ref, plans[0]),
            "priority": "high" if total >= 500 else ("medium" if total >= 100 else "low"),
        })

    # 按金额降序
    aggregated.sort(key=lambda x: -x["total_amount"])
    return aggregated


# ── 消息生成 ───────────────────────────────────────────────────────────────────
def generate_messages(aggregated: list[dict]) -> list[dict]:
    """为每个聚合客户生成最优消息（合并版优先）"""
    messages = []
    for agg in aggregated:
        ref = agg["ref"]
        total = agg["total_amount"]
        link = agg["pay_link"]
        orders = agg["orders"]

        if agg["kind"] == "combined" and total >= 200:
            # 合并版：高价值客户用汇总消息
            lines = []
            for o in orders:
                plan_name = {"proY": "专业·年度", "team": "团队·年度", "pro3": "专业·季度",
                             "pro": "专业·月度", "corp": "年费对公"}.get(o["plan"], o["plan"])
                lines.append(f"• {plan_name} — ¥{int(o['amount'])}")
            msg = render_template("summary_combined",
                                  total=int(total),
                                  order_lines="\n".join(lines),
                                  link=link)
        elif orders[0]["kind"] == "corp":
            o = orders[0]
            msg = render_template("corporate_remittance",
                                  oid=o["order_id"], ref=ref, amt=int(o["amount"]),
                                  memo=o.get("memo", ""))
        elif orders[0]["kind"] == "trial":
            days = int(orders[0].get("days_ago", 7))
            msg = render_template("trial_winback", days=days, link=link)
        else:
            o = orders[0]
            msg = render_template("single_order",
                                  oid=o["order_id"], ref=ref,
                                  amt=int(o["amount"]), link=link)

        messages.append({
            "ref": ref,
            "total_amount": total,
            "priority": agg["priority"],
            "message": msg,
            "pay_link": link,
            "order_count": agg["order_count"],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        })
    return messages


# ── 工作流 ──────────────────────────────────────────────────────────────────────
async def run_collection_workflow(billing_dir: str = "/opt/bingdashan/data/billing",
                                   output_dir: str = "/tmp/outreach") -> dict:
    """完整收款自动化工作流"""
    from pathlib import Path as P
    out = P(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    log.info("=== Collection Workflow Start ===")

    # Step 1: 扫描
    aggregated = scan_all_pending(billing_dir)
    log.info(f"Found {len(aggregated)} unique customers, total ¥{sum(a['total_amount'] for a in aggregated):,.0f}")

    # Step 2: 生成消息
    messages = generate_messages(aggregated)
    total_recovery = sum(m["total_amount"] for m in messages)

    # Step 3: 导出
    result = {"generated_at": datetime.now(timezone.utc).isoformat(),
              "total_customers": len(messages), "total_amount_yuan": total_recovery,
              "messages": messages}
    (out / "collection_messages.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    # TXT 格式（方便复制）
    txt_lines = [f"# 💰 收款消息包 ({len(messages)} 人, 总计 ¥{total_recovery:,.0f})\n\n"]
    for i, m in enumerate(messages, 1):
        txt_lines.append(f"--- #{i} · {m['ref']} · ¥{m['total_amount']:.0f} [{m['priority']}] ---\n")
        txt_lines.append(m["message"] + "\n\n")
    (out / "collection_messages.txt").write_text("".join(txt_lines), encoding="utf-8")

    # CSV format for Excel
    csv_lines = ["ref,total_amount,priority,pay_link\n"]
    for m in messages:
        csv_lines.append("{},{:.0f},{},{}\n".format(
            m["ref"], m["total_amount"], m["priority"], m["pay_link"]))
    (out / "collection_messages.csv").write_text("".join(csv_lines), encoding="utf-8")

    log.info(f"Messages exported → {out}")
    log.info(f"Total recoverable: ¥{total_recovery:,.0f}")
    return result


if __name__ == "__main__":
    import asyncio
    billing = sys.argv[1] if len(sys.argv) > 1 else "/opt/bingdashan/data/billing"
    result = asyncio.run(run_collection_workflow(billing))
    print(f"\n✅ 生成 {result['total_customers']} 条消息，总计 ¥{result['total_amount_yuan']:,.0f}")

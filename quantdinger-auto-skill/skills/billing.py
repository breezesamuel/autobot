#!/usr/bin/env python3
"""billing skill — 收款自动化：批量生成消息、发送提醒、追踪状态"""

from __future__ import annotations
import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

# ─── 常量 ──────────────────────────────────────────────────────────────────────
BASE_URL = "https://tools-cn.highkingflower.com"
REF_PREFIX = "丙大山"


# ─── 模板引擎 ──────────────────────────────────────────────────────────────────
TEMPLATES = {
    "proY_annual": (
        "客户您好，您 10 月意向的【专业·年度 366天】我们为您保留名额。"
        "这是您的专属开通链接，点它付款即开通 + 赠 30 天优先支持："
        "{link} （大额支持分期/对公，可回我协助。限时 48h，本季最低价 ¥{amt}，"
        "历史回测不代表未来收益，付款前请确认需求。）"
    ),
    "team_annual": (
        "客户您好，您 10 月意向的【团队·年度 366天】我们为您保留名额。"
        "这是您的专属开通链接，点它付款即开通 + 赠 30 天优先支持："
        "{link} （大额支持分期/对公，可回我协助。限时 48h，本季最低价 ¥{amt}，"
        "历史回测不代表未来收益，付款前请确认需求。）"
    ),
    "quarterly": (
        "您好，您选的【专业·季度 93天】还差最后一步。专属链接在此，"
        "付款即开通：{link} （限时 48h，附赠 1 份专业回测报告(C3)。"
        "¥{amt}，非投资建议，历史回测不代表未来收益。）"
    ),
    "monthly": (
        "您的月度订阅即将到期，续费享 9 折优惠："
        "{link} （¥{amt}/月，解锁全部工具 + 行情数据订阅。）"
    ),
    "trial_winback": (
        "您的 7 天体验已结束。解锁全部工具 + 专业回测报告(C3) + "
        "行情数据订阅，专业月度 ¥60/31天，限时新用户 9 折。"
        "专属升级链接: {link}"
    ),
    "corporate_remittance": (
        "【丙大山·年费¥{amt} 对公打款】\n"
        "订单号: {oid}\n金额: ¥{amt}\n"
        "汇款备注: 丙大山年付-{oid}-{ref}\n"
        "收款账户：以正式对公函为准（见运营附件）。"
    ),
}


def build_pay_link(ref: str, plan: str, slug: str = "tool") -> str:
    """生成带有 ref 参数的支付链接"""
    return f"{BASE_URL}/api/pay?plan={plan}&slug={slug}&ref={ref}"


def generate_message(order: dict) -> str:
    """根据订单类型生成个性化消息"""
    kind = order.get("kind", "").lower()
    amt = int(float(order.get("amount", 0) or order.get("collect", 0)))
    ref = order.get("ref", "")
    oid = order.get("order_id", order.get("id", ""))[:20]

    if "corp" in kind or "corporate" in kind:
        tpl = TEMPLATES["corporate_remittance"]
        return tpl.format(amt=amt, oid=oid, ref=ref)

    # Trial winback → 使用专用模板（含"体验"/"升级"关键词）
    if kind == "trial":
        link = build_pay_link(ref, "pro")
        return TEMPLATES["trial_winback"].format(link=link)

    plan = order.get("plan", "proY")
    link = build_pay_link(ref, plan)

    if plan == "proY":
        tpl = TEMPLATES["proY_annual"]
    elif plan == "team":
        tpl = TEMPLATES["team_annual"]
    elif plan in ("pro3", "q"):
        tpl = TEMPLATES["quarterly"]
    elif plan == "pro":
        tpl = TEMPLATES["monthly"]
    else:
        tpl = TEMPLATES["proY_annual"]

    return tpl.format(link=link, amt=amt)


def parse_billing_tsv(tsv_path: str | Path) -> list[dict]:
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
                row["amount"] = float(row.get("amount", 0) or 0)
                row["kind"] = row.get("plan", "?")
                rows.append(row)
    return rows


def scan_pending_orders(billing_dir: str | Path = "/opt/bingdashan/data/billing") -> list[dict]:
    """扫描所有待收款订单，按金额排序"""
    bd = Path(billing_dir)
    pending = []

    # manual_8
    try:
        tsv = bd / "manual_pending.tsv"
        for r in parse_billing_tsv(tsv):
            if float(r.get("amount", 0)) > 0:
                pending.append({
                    "source": "manual_8",
                    "order_id": r.get("id", ""),
                    "ref": r.get("visitor", "").split(":")[-1] if ":" in r.get("visitor", "") else r.get("id", ""),
                    "amount": float(r.get("amount", 0)),
                    "plan": r.get("plan", "m"),
                    "kind": "manual",
                    "ip": r.get("visitor", "").split(":")[0].replace("ip:", "") if ":" in r.get("visitor", "") else "",
                })
    except Exception:
        pass

    # corporate_899
    try:
        corp = json.loads((bd / "corporate_899.json").read_text())
        for r in (corp if isinstance(corp, list) else corp.get("orders", [])):
            pending.append({
                "source": "corporate_899",
                "order_id": r.get("order_id", ""),
                "ref": r.get("ref", ""),
                "amount": float(r.get("corporate_amount", r.get("amount", 899))),
                "plan": "y",
                "kind": "corp",
            })
    except Exception:
        pass

    # trial_winback
    try:
        tsv = bd / "trial_winback.tsv"
        for r in parse_billing_tsv(tsv):
            pending.append({
                "source": "trial_winback",
                "order_id": r.get("ref", ""),
                "ref": r.get("ref", ""),
                "amount": 60.0,
                "plan": "pro",
                "kind": "trial",
                "days_ago": float(r.get("距今天", 0) or 0),
            })
    except Exception:
        pass

    # 按金额降序排列
    pending.sort(key=lambda x: -x["amount"])
    return pending


def export_messages(orders: list[dict], out_dir: str | Path = "/tmp/outreach") -> dict:
    """导出消息包到 JSON + TXT"""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    messages = []
    for o in orders:
        msg = generate_message(o)
        messages.append({
            "ref": o["ref"],
            "amount": o["amount"],
            "kind": o["kind"],
            "source": o["source"],
            "message": msg,
            "pay_link": build_pay_link(o["ref"], o["plan"]),
        })

    total = sum(m["amount"] for m in messages)

    # JSON
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_pending": len(messages),
        "total_amount_yuan": total,
        "messages": messages,
    }
    (out / "collection_messages.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # TXT
    lines = [f"# 💰 收款消息包 ({len(messages)} 条, 总计 ¥{total:.0f})\n",
             f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"]
    for i, m in enumerate(messages, 1):
        lines.append(f"--- #{i} · {m['ref']} · ¥{m['amount']:.0f} ---\n")
        lines.append(m["message"] + "\n\n")

    (out / "collection_messages.txt").write_text("".join(lines), encoding="utf-8")

    return result


# ─── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    billing_dir = sys.argv[1] if len(sys.argv) > 1 else "/opt/bingdashan/data/billing"
    orders = scan_pending_orders(billing_dir)
    result = export_messages(orders)
    print(f"共 {result['total_pending']} 条待收消息，总金额 ¥{result['total_amount_yuan']:.0f}")
    print(f"JSON: collection_messages.json")
    print(f"TXT:  collection_messages.txt")

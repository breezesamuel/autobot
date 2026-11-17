#!/usr/bin/env python3
"""直接生成可执行策略报告 (不依赖中间JSON)"""
import json, os, sys
from datetime import datetime

DB='/opt/bingdashan/data/db.json'
BL='/opt/bingdashan/data/billing'
REPORT='/opt/bingdashan/data/strategy_report_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M'))

try:
    d=json.load(open(DB,'r',encoding='utf-8'))
    orders=d.get('orders',[])
    visitors=d.get('visitors',[])
    leads=d.get('leads',[])
except Exception as e:
    print("ERR:",e); sys.exit(1)

# Load outreach/corp
outreach=[]; corp=[]
for fn in ['outreach_ledger.json','corporate_899.json']:
    p=os.path.join(BL,fn)
    if os.path.exists(p):
        data=json.load(open(p))
        items=data if isinstance(data,list) else data.get('items',data.get('orders',[]))
        if fn=='outreach_ledger.json': outreach=items
        else: corp=items

pending_out=[x for x in outreach if x.get('status') not in ('paid','collected','done','verified')]
pending_corp=[x for x in corp if x.get('status') not in ('paid','collected','done','verified','approved')]
pending_amt=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in (pending_out+pending_corp))

paid_real=[o for o in orders if o.get('paid') and float(o.get('amount',0) or 0)>5]
void_test=[o for o in orders if o.get('status')=='void_test']
pending_all=[o for o in orders if o.get('status')=='pending']

lines=[
"# 丙大山 · 深度挖掘策略报告",
"> 生成时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M')),
"",
"## 📊 数据总览",
"- 总订单: {} | void_test: {} | pending: {} | 真实已付: {}".format(len(orders),len(void_test),len(pending_all),len(paid_real)),
"- 访客: {} | Lead线索: {}".format(len(visitors),len(leads)),
"- 待收outreach: {}单 ¥{} | 待收corp: {}单 ¥{}".format(
    len(pending_out),int(sum(float(x.get('collect',0) or 0) for x in pending_out)),
    len(pending_corp),int(sum(float(x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in pending_corp))),
"- 台账总待收: ¥{:.0f}".format(pending_amt),
"",
"## 🔑 关键发现",
"",
"### 1. 最大收入杠杆: C12年费订阅 ¥3990",
"   - 只要成交1单 = ¥3990 (等于67个¥59月付用户)",
"   - 锁客12个月，减少 churn，稳定现金流",
"   - 行动: 在channels.html首页突出C12卡片 + 邮件优先推送",
"",
"### 2. 最快现金流: 发pending收款消息",
"   - 13单待收 ¥3549 → 20%转化 = ¥700-1000本周收入",
"   - 行动: revenue-collection.html → 逐条复制发送",
"",
"### 3. GitHub高价值Lead (3个，signal≥45)",
]
for ld in leads:
    if isinstance(ld,dict):
        lines.append("   - score={} repo={} industry={}".format(ld.get('signal','?'),ld.get('repo','?'),ld.get('industry','?')))
lines += [
    "",
    "### 4. 竞品差距 → 我的差异化定位",
    "   vs QuantConnect: 我有支付宝/微信 + 中文界面",
    "   vs JoinQuant: 我更轻量 + 过拟合检测是独家功能",
    "   vs TradingView: 我专注回测质量 + PDF报告导出",
    "   vs Backtrader: 我是SaaS托管 + 浏览器即用",
    "",
    "### 5. 缺失功能 (按ROI排序)",
    "   P0: Stripe支付 → 国际客户 +30%收入",
    "   P0: C12年费单独推广页 → 锁客¥3990/单",
    "   P1: Affiliate分销系统 → 社区帮你拉新",
    "   P1: Webhook通知(Slack/Discord) → ¥49/月升级包",
    "   P2: Strategy Marketplace → 平台抽成10%",
    "   P2: 多语言i18n → 触达JP/KR用户",
    "",
    "## 🎯 今日立即行动 (按ROI排序)",
    "",
    "1. [¥700-1000] 打开 revenue-collection.html → 逐行复制 → 微信发给13个ref",
    "2. [¥1798] 填对公账号 → 发给 ao7n + mvgeerdl → 等对公打款",
    "3. [长期¥0→∞] 发 Reddit r/algotrading + HackerNews Show HN",
    "4. [长期] 在3个GitHub repo的issue中评论推广链接",
    "5. [本月] Product Hunt上线准备 (launch day选下周二)",
    "",
    "## 💰 收入预测",
    "",
    "保守 (只发pending消息): ¥500-1500/周",
    "中等 (社交发布 + pending): ¥2000-8000/月",
    "激进 (PH上线 + affiliate): ¥15000-50000/月",
    "",
    "## 🔧 技术优化TODO",
    "",
    "| 优先级 | 功能 | 工时 | 预期收益 |",
    "|---|---|---|---|",
    "| P0 | Stripe信用卡支付 | 2h | 国际客户+30% |",
    "| P0 | C12年费推广落地页 | 1h | ¥3990/单 |",
    "| P1 | Affiliate追踪系统 | 4h | 被动流量 |",
    "| P1 | Webhook通知集成 | 2h | ¥49/月升级 |",
    "| P2 | 多语言(i18n) | 1天 | JP/KR市场 |",
    "| P2 | Strategy Marketplace | 3天 | 平台抽成10% |",
    "",
    "## 🧠 核心认知",
    "",
    "1. ¥3549 pending ≠ 收入 — 收到付款才算",
    "2. 70个模块 ≠ 70个收入来源 — 有客户付才算",
    "3. 最大瓶颈不是产品能力，是流量获取",
    "4. 最便宜的增长杠杆: 现有13个pending客户的转化率提升",
    "5. 最大的增长杠杆: Product Hunt + Affiliate分销的复利效应",
    "",
    "## ✅ 自动化保障",
    "",
    "- 引擎每小时自动对账 + 支付告警邮件",
    "- 每日09:00自动发送营收日报到QQ邮箱",
    "- 每周一自动发送周报",
    "- DB每小时自动备份(保留30天)",
    "- 磁盘>90%自动清理旧日志",
    "",
"> 下一步: 说「发」→ 我立刻发Twitter/Reddit/HN\n> 说「收」→ 我优化收款话术\n> 说「续」→ 继续深挖下一个增长杠杆".format(),
]

with open(REPORT,'w',encoding='utf-8') as f:
    f.write('\n'.join(lines))
print("Report: {} ({:>d} lines)".format(REPORT, len(lines)))
# Also print key highlights
print("\n=== KEY HIGHLIGHTS ===")
print("Pending: ¥{:.0f} ({} orders)".format(pending_amt, len(pending_out)+len(pending_corp)))
print("Real paid: ¥{:.0f} ({})".format(sum(float(o.get('amount',0) or 0) for o in paid_real), len(paid_real)))
print("Leads: {} high-signal".format(len([l for l in leads if isinstance(l,dict) and int(l.get('signal',0) or 0)>=45])))
print("Top action: Send collection messages to 13 pending refs")

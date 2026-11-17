#!/usr/bin/env python3
"""丙大山 · 收款话术优化引擎 — 生成高转化率催付消息"""
import json,os,sys
from datetime import datetime
from collections import defaultdict

BL='/opt/bingdashan/data/billing'
DB='/opt/bingdashan/data/db.json'
OUT_DIR='/opt/bingdashan/data/outreach_autogen'
LOG='/var/log/bingdashan/optimize_collection.log'
os.makedirs(OUT_DIR, exist_ok=True)

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[COL][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Collection Message Optimizer ===")

# Load pending orders
outreach_items=[]; corp_items=[]
for fn in ['outreach_ledger.json','corporate_899.json']:
    fp=os.path.join(BL,fn)
    if not os.path.exists(fp): continue
    data=json.load(open(fp))
    items=data if isinstance(data,list) else data.get('items',data.get('orders',[]))
    if fn=='outreach_ledger.json': outreach_items=items
    else: corp_items=items

pending_out=[x for x in outreach_items if x.get('status') not in ('paid','collected','done','verified')]
pending_corp=[x for x in corp_items if x.get('status') not in ('paid','collected','done','verified','approved')]

# Group by ref for personalized messaging
ref_messages=defaultdict(lambda:{'outreach':[],'corp':[],'total':0})
for x in pending_out:
    ref=x.get('ref','')
    amt=float(x.get('collect',0) or 0)
    ref_messages[ref]['outreach'].append(x)
    ref_messages[ref]['total']+=amt
for x in pending_corp:
    ref=x.get('ref','')
    amt=float(x.get('amount',0) or x.get('corporate_amount',0) or 0)
    ref_messages[ref]['corp'].append(x)
    ref_messages[ref]['total']+=amt

# Generate optimized messages
optimized_msgs=[]
for ref,msgs in sorted(ref_messages.items(),key=lambda x:-x[1]['total'])[:15]:
    total=msgs['total']
    oid_list=[str(x.get('order_id',''))[:12] for x in msgs['outreach']+msgs['corp']]
    
    # Dynamic message based on amount and ref history
    if total>=1000:
        # High value - use urgency + scarcity
        msg="""【丙大山·重要提醒】您的账户有待确认订单。

📋 订单汇总:
  • 金额: ¥{amt}
  • 订单号: {oids}

⏰ 限时优惠: 本周内完成支付，额外赠送3份专业报告(C3)。
💳 支付宝直连: https://tools-cn.highkingflower.com/api/pay?plan=proY&slug=tool&ref={ref}
🏦 对公打款: 请联系客服获取账号信息

⚠️ 注意: 回测是历史数据，不代表未来收益；非投资建议，风险自负。
""".format(amt=int(total),oids=', '.join(oid_list[:3]),ref=ref)
    elif total>=500:
        # Medium value - benefit-focused
        msg="""【丙大山·支付提醒】您有¥{amt}的订单待开通。

✨ 开通后您将解锁:
  • 70+专业量化工具
  • 真实币安K线回测
  • 过拟合检测(独家功能)
  • 一键导出PDF专业报告
  • 7×24技术支持

💳 立即开通: https://tools-cn.highkingflower.com/api/pay?plan=proY&slug=tool&ref={ref}

⚠️ 注意: 回测是历史数据，不代表未来收益；非投资建议，风险自负。
""".format(amt=int(total),ref=ref)
    else:
        # Low value - quick action
        msg="""【丙大山·支付提醒】您的订单 ¥{amt} 已准备好。

💳 点击链接立即开通: https://tools-cn.highkingflower.com/api/pay?plan=pro&slug=tool&ref={ref}

开通后即可使用全部70+量化回测工具。
⚠️ 注意: 回测是历史数据，不代表未来收益；非投资建议，风险自负。
""".format(amt=int(total),ref=ref)
    
    optimized_msgs.append({
        'ref': ref, 'total': int(total), 'message': msg,
        'priority': 'high' if total>=500 else 'medium',
        'generated_at': datetime.now().isoformat()
    })

# Save to file
if optimized_msgs:
    out_path=os.path.join(OUT_DIR,'optimized_collection_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M')))
    with open(out_path,'w',encoding='utf-8') as f:
        f.write("# 丙大山 · 优化版收款消息 (自动生成)\n")
        f.write("> 生成时间: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M')))
        f.write("> 共{}条，按优先级排序，逐条复制到微信/QQ发送\n\n".format(len(optimized_msgs)))
        for i,m in enumerate(optimized_msgs,1):
            f.write("--- 第{}条 | Ref:{} | ¥{} ---\n".format(i,m['ref'],m['total']))
            f.write(m['message'])
            f.write("\n\n")
    log("Saved {} optimized messages -> {}".format(len(optimized_msgs), out_path))

# Also generate WeChat-friendly short versions
short_msgs=[]
for m in optimized_msgs:
    short=m['message'].replace('【丙大山·重要提醒】','').replace('【丙大山·支付提醒】','').strip()
    short_msgs.append({'ref':m['ref'],'total':m['total'],'short':short[:200]})

short_path=os.path.join(OUT_DIR,'wechat_short_messages_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M')))
with open(short_path,'w',encoding='utf-8') as f:
    f.write("# 丙大山 · 微信快捷版消息\n")
    f.write("> 复制后直接粘贴到微信聊天框\n\n")
    for sm in short_msgs[:10]:
        f.write("[Ref:{} ¥{}]\n{}".format(sm['ref'],sm['total'],sm['short'][:150]))
        f.write("\n\n")
log("Saved WeChat short messages -> {}".format(short_path))

# Summary
total_potential=sum(m['total'] for m in optimized_msgs)
high_priority=len([m for m in optimized_msgs if m['priority']=='high'])
log("Total potential collection: ¥{}".format(total_potential))
log("High priority refs: {}".format(high_priority))
log("=== Collection Optimizer Complete ===")
print(json.dumps({'messages':len(optimized_msgs),'potential':int(total_potential),'high_priority':high_priority},ensure_ascii=False))

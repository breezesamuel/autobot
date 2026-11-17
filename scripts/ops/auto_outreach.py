#!/usr/bin/env python3
"""自动触达脚本: 为每个 pending_outreach/corp 订单生成个性化微信消息并写文件 (供运营复制)"""
import json, os, sys
from datetime import datetime

BL='/opt/bingdashan/data/billing'
OUT_JSON='/opt/bingdashan/data/outreach_messages.json'
OUT_TXT='/opt/bingdashan/data/outreach_messages.txt'
LOG='/var/log/bingdashan/outreach.log'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[OUTREACH][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Outreach Generator start ===")
# Load orders
outreach=[]
try:
    d=json.load(open(os.path.join(BL,'outreach_ledger.json')))
    outreach=d if isinstance(d,list) else d.get('items',[])
except Exception as e:
    log("ERR load outreach: {}".format(e)); sys.exit(1)
corp=[]
try:
    d=json.load(open(os.path.join(BL,'corporate_899.json')))
    corp=d if isinstance(d,list) else d.get('items',d.get('orders',[]))
except Exception as e:
    log("ERR load corp: {}".format(e))

FINAL={'paid','collected','done','verified','approved'}
pending=[x for x in outreach if isinstance(x,dict) and x.get('status') not in FINAL]
pending += [x for x in corp if isinstance(x,dict) and x.get('status') not in FINAL]

messages=[]
for n, idx in enumerate(pending, start=1):
    oid=str(idx.get('order_id',''))[:20]
    ref=str(idx.get('ref',''))
    amt=float(idx.get('collect',0) or idx.get('amount',0) or idx.get('corporate_amount',0) or 0)
    kind=str(idx.get('kind','?'))
    link=str(idx.get('pay_link','') or '')
    note=str(idx.get('note','') or idx.get('memo','') or '')
    
    if 'corp' in kind.lower() or 'corporate' in str(idx).lower():
        memo=idx.get('remit_memo','丙大山年付-{}-{}'.format(oid,ref))[:40]
        msg="【丙大山·年费¥{} 对公打款】\n订单号:{}\n金额:¥{}\n汇款备注:{}".format(int(amt),oid,int(amt),memo)
        if link: msg+="\n支付宝备选: {}".format(link)
        msg+="" \
            "\n收款账户：以正式对公函为准（见运营附件）。\n" \
            "注意: 对公打款需备注订单号，便于核销。"
    else:
        msg="【丙大山·支付提醒】\n您的订单 {} 已开通。\n付款链接: {}\n金额: ¥{}\n注意: 回测是历史数据，不代表未来收益；非投资建议，风险自负。".format(oid, link or '-', int(amt))
    
    messages.append({
        'index': n,
        'order_id': oid,
        'ref': ref,
        'amount': int(amt),
        'kind': kind,
        'message': msg,
        'generated_at': datetime.now().isoformat()
    })

result={'total_pending': len(messages), 'generated_at': datetime.now().isoformat(), 'messages': messages}
with open(OUT_JSON,'w',encoding='utf-8') as f:
    json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')

txt_lines=["# 丙大山 · 待触达客户消息包 ({} 条)\n".format(len(messages))]
txt_lines.append("> 生成时间: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
txt_lines.append("> 说明: 每条消息可复制到微信/QQ/短信直接发送。\n\n")
for m in messages:
    txt_lines.append("--- 第 {} 条 ---\n".format(m['index']))
    txt_lines.append("订单ID: {}\n类型: {}\n金额: ¥{}\n消息:\n{}\n\n".format(m['order_id'], m['kind'], m['amount'], m['message']))
with open(OUT_TXT,'w',encoding='utf-8') as f:
    f.writelines(txt_lines)

log("Generated {} outreach messages -> {} + {}".format(len(messages), OUT_JSON, OUT_TXT))
for m in messages:
    log("  #{} ref={} amt=¥{} kind={}".format(m['index'], m['ref'], m['amount'], m['kind']))
log("=== Outreach Generator done ===")

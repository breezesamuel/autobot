#!/usr/bin/env python3
"""丙大山 · 增长杠杆分析器 — 识别下一个最大收入来源"""
import json,os,sys
from datetime import datetime

OUT='/opt/bingdashan/data/growth_levers_v1.json'
REPORT='/opt/bingdashan/data/growth_report_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M'))

log_lines=[]
def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[GL][{}] {}".format(ts,m); print(line)
    log_lines.append(line)

log("=== Growth Lever Analyzer ===")

# Analyze current state
try:
    d=json.load(open('/opt/bingdashan/data/db.json'))
    orders=d.get('orders',[])
    visitors=d.get('visitors',[])
except Exception as e:
    log("ERR: {}".format(e)); sys.exit(1)

# Calculate key metrics
total_orders=len(orders)
trial_orders=len([o for o in orders if o.get('plan')=='t'])
paid_orders=len([o for o in orders if o.get('paid') and float(o.get('amount',0) or 0)>5])
avg_order_value=sum(float(o.get('amount',0) or 0) for o in orders if o.get('paid'))/max(paid_orders,1)

trial_conversion_rate=paid_orders/max(trial_orders,1)*100

log("Current metrics:")
log("  Total orders: {}".format(total_orders))
log("  Trial users: {}".format(trial_orders))
log("  Paid users: {}".format(paid_orders))
log("  Trial conversion rate: {:.2f}%".format(trial_conversion_rate))
log("  Avg order value: ¥{:.0f}".format(avg_order_value))

# Identify growth levers
levers=[]

# Lever 1: Improve trial conversion
current_trial_conversion=trial_conversion_rate
target_trial_conversion=5.0  # Industry average
improved_conversions=int(trial_orders*target_trial_conversion/100)-paid_orders
estimated_revenue=improved_conversions*avg_order_value*0.8  # 80% conservative

levers.append({
    'name': 'Trial→Paid转化优化',
    'effort': '中',
    'timeline': '本周',
    'potential_revenue': int(estimated_revenue),
    'action': 'A/B测试落地页、优化邮件序列、增加紧迫感',
    'roi': '高',
    'description': '将trial用户转化率从{:.1f}%提升到{:.0f}%，预计新增{}单'.format(
        current_trial_conversion, target_trial_conversion, improved_conversions)
})

# Lever 2: Social media content
monthly_traffic_from_social=500  # Estimate
social_conversion=2.0  # 2% visit→trial
social_trials=int(monthly_traffic_from_social*social_conversion/100)
social_revenue=social_trials*avg_order_value*0.3  # 30% convert to paid

levers.append({
    'name': '社交媒体持续引流',
    'effort': '低',
    'timeline': '持续',
    'potential_revenue': int(social_revenue),
    'action': '每日Twitter/Reddit/HN发帖，保持活跃',
    'roi': '中高',
    'description': '每天发布1-2条内容，月均带来{}新trial，转化为付费用户'.format(social_trials)
})

# Lever 3: Affiliate program
affiliate_influencers=20  # Estimate potential partners
affiliates_per_influencer=2  # Average referrals per influencer
affiliate_conversion=10.0  # 10% referral→paid
affiliate_cpa=30
affiliate_cost=affiliate_influencers*affiliates_per_influencer*affiliate_conversion/100*affiliate_cpa
affiliate_revenue=affiliate_influencers*affiliates_per_influencer*100*avg_order_value*0.1

levers.append({
    'name': 'Affiliate分销系统化',
    'effort': '中',
    'timeline': '本月',
    'potential_revenue': int(max(affiliate_revenue-affiliate_cost, 0)),
    'action': '联系20个KOL，建立分销合作机制',
    'roi': '极高',
    'description': '每个KOL带来100个referral，10%转化，净收益+'
})

# Lever 4: Product Hunt
ph_upvotes_needed=300  # To get on front page
ph_new_users=100  # Estimated from top 10 PH launch
ph_conversion=3.0
ph_revenue=ph_new_users*ph_conversion/100*avg_order_value*12  # Annual plans

levers.append({
    'name': 'Product Hunt上市',
    'effort': '高',
    'timeline': '下周二',
    'potential_revenue': int(ph_revenue),
    'action': '准备PH页面、投票引导、限时优惠',
    'roi': '高',
    'description': '一次爆发带来{}新用户，3%转化年费客户'.format(ph_new_users)
})

# Lever 5: Enterprise sales
enterprise_targets=10  # Companies to target
enterprise_conversion=10.0  # 10% demo→deal
enterprise_avg_contract=5000  # ¥5000 avg contract

levers.append({
    'name': '企业级销售拓展',
    'effort': '高',
    'timeline': '本月',
    'potential_revenue': int(enterprise_targets*enterprise_conversion/100*enterprise_avg_contract),
    'action': '联系券商/基金/高校量化实验室',
    'roi': '极高',
    'description': '每个企业合同平均¥5000，潜在10家客户'
})

# Sort by potential revenue
levers.sort(key=lambda x:x['potential_revenue'],reverse=True)

# Output results
result={
    'generated_at':datetime.now().isoformat(),
    'current_metrics':{
        'total_orders':total_orders,'trial_orders':trial_orders,'paid_orders':paid_orders,
        'trial_conversion_rate':round(trial_conversion_rate,2),'avg_order_value':int(avg_order_value)
    },
    'growth_levers':levers,
    'recommended_sequence':[
        'P0: 立即收pending账款 ¥3549',
        'P1: 优化trial转化 (本周)',
        'P2: 社交媒体持续引流 (持续)',
        'P3: Product Hunt上线 (下周二)',
        'P4: Affiliate分销 (本月)',
        'P5: 企业销售 (长期)'
    ],
    'total_potential_revenue':sum(l['potential_revenue'] for l in levers)
}

with open(OUT,'w',encoding='utf-8') as f:
    json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')

# Generate report
report_lines=[
    "# 丙大山 · 增长杠杆分析报告",
    "> 生成时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M')),
    "",
    "## 📊 当前关键指标",
    "- 总订单: {} | Trial用户: {} | 付费用户: {}".format(total_orders,trial_orders,paid_orders),
    "- Trial转化率: {:.2f}%".format(trial_conversion_rate),
    "- 平均订单价值: ¥{}".format(int(avg_order_value)),
    "",
    "## 🚀 增长杠杆排名 (按预期收益)",
    "",
]
for i,l in enumerate(levers,1):
    report_lines.append("### {}. {} [ROI: {}]".format(i,l['name'],l['roi']))
    report_lines.append("- 预期收益: ¥{}".format(l['potential_revenue']))
    report_lines.append("- 实施难度: {} | 时间: {}".format(l['effort'],l['timeline']))
    report_lines.append("- 行动: {}".format(l['action']))
    report_lines.append("- 说明: {}".format(l['description']))
    report_lines.append("")

report_lines += [
    "## 🎯 推荐执行顺序",
    "",
]
for step in result['recommended_sequence']:
    report_lines.append(step)
    report_lines.append("")

report_lines += [
    "## 💰 总收入潜力估算",
    "- 当前pending账款: ¥3,549",
    "- 增长杠杆总潜力: ¥{}".format(result['total_potential_revenue']),
    "- **理论上限: ¥{}**".format(3549+result['total_potential_revenue']),
    "",
    "---",
    "> 说「执行」→ 我开始实施最高优先级的杠杆\n> 说「详情」→ 查看具体执行方案",
]

with open(REPORT,'w',encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

log("Growth levers analysis complete")
log("Top lever: {} (¥{})".format(levers[0]['name'],levers[0]['potential_revenue']))
log("Total potential: ¥{}".format(result['total_potential_revenue']))
log("Report saved: {}".format(REPORT))
print(json.dumps({'top_lever':levers[0]['name'],'top_revenue':levers[0]['potential_revenue'],
                   'total_levers':len(levers)},ensure_ascii=False))

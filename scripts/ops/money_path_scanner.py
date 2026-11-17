#!/usr/bin/env python3
"""丙大山 · 赚钱路径扫描引擎 v1 (穷举式发现所有可变现点)"""
import json, os, sys, re
from datetime import datetime

ROOT='/www/wwwroot/tools-cn.highkingflower.com'
LIB_DIR=os.path.join(ROOT,'lib')
API_DIR=os.path.join(ROOT,'api')
LOG='/var/log/bingdashan/pathfinder.log'
OUTPUT='/opt/bingdashan/data/money_paths.json'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[PF][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Money Path Scanner v1 start ===")
paths=[]

# ===== Category 1: Code-level monetization (each function in lib/*.js can be a separate charge point) =====
for fn in os.listdir(LIB_DIR):
    if not fn.endswith('.js'): continue
    fpath=os.path.join(LIB_DIR,fn)
    try:
        src=open(fpath,'r',encoding='utf-8').read()
    except: continue
    # 找 async function 作为独立计费单元
    funcs=re.findall(r'async\s+function\s+(\w+)',src)
    funcs += re.findall(r'const\s+(\w+)\s*=\s*async\s*\(',src)
    # 找参数/定价变量
    prices=re.findall(r'PRICE[_\w]+\s*=\s*(?:process\.env\.)?(\w+|\d+)',src)
    for func in set(funcs):
        paths.append({
            'category':'code_function',
            'module':fn.replace('.js',''),
            'function':func,
            'current_pricing':'via '+(','.join(prices[:3]) if prices else 'unknown'),
            'potential':'单一function调用收费 (按次/按量)'
        })

# ===== Category 2: Report format extensions (each output format = new SKU) =====
report_formats=['PDF','CSV','JSON','Excel','Markdown','HTML','PNG','YAML']
for fmt in report_formats:
    paths.append({
        'category':'report_format',
        'module':'reportexport',
        'feature':'输出格式 {}'.format(fmt),
        'pricing_hint':'$2-5 per export, or bundle into tiered plans',
        'priority':'medium'
    })

# ===== Category 3: Data subscription tiers (granular data access) =====
data_tiers=[
    ('daily_klines','日线K线数据订阅','¥29/月'),
    ('minute_klines','分钟级K线数据订阅','¥99/月'),
    ('tick_data','逐笔成交数据订阅','¥299/月'),
    ('futures_data','期货/期权数据订阅','¥199/月'),
    ('alternative_data','另类数据 (链上/社交/新闻)','¥499/月'),
    ('custom_indicators','自定义指标库访问','¥49/月'),
    ('backtest_history','历史回测结果存档','¥19/月'),
    ('strategy_marketplace','策略市场发布佣金抽成','每单10%'),
]
for item in data_tiers:
    paths.append({
        'category':'data_subscription',
        'module':'marketdata',
        'feature':item[0],
        'desc':item[1],
        'pricing_hint':item[2],
        'priority':'high'
    })

# ===== Category 4: User tier expansion (upsell existing users) =====
tier_model=[
    ('free_trial','7天免费试用','现有机制，维持'),
    ('pro_monthly','专业版月付 ¥60','已有，可增加功能包'),
    ('pro_yearly','专业版年付 ¥500 (8折)','已有'),
    ('team_seat','团队席位 ¥299/席/年','C8已有但没推'),
    ('api_access','API调用包 ¥199/1000次','可从C4拆分出来'),
    ('white_label','白标授权 ¥1999/起','C8已有但未宣传'),
    ('enterprise','企业定制 ¥5000+/项目','全新高客单价'),
    ('consulting','量化咨询 ¥500/小时','人工服务高毛利'),
]
for item in tier_model:
    paths.append({
        'category':'user_tier',
        'module':'subwall',
        'feature':item[0],
        'desc':item[1],
        'pricing_hint':item[2],
        'priority':'high' if item[2].startswith('¥') and int(re.search(r'\d+',item[2]) or '0')>100 else 'medium'
    })

# ===== Category 5: API productization (turn functions into REST API endpoints with usage-based pricing) =====
api_candidates=[
    ('backtest_api','单次回测API','按调用次数收费','C10 already does this'),
    ('overfit_api','过拟合检测API','按次收费','C7 already does this'),
    ('combo_api','多资产组合API','按组合数收费','C9 already does this'),
    ('scan_api','全市场扫描API','按扫标的收费','全新'),
    ('optimize_api','参数优化API','按优化组数收费','全新'),
    ('paper_trade_api','纸面交易执行API','按交易次数收费','全新'),
    ('alert_api','价格预警通知API','按通知条数收费','全新'),
    ('portfolio_api','组合绩效分析API','按月收费','全新'),
]
for item in api_candidates:
    paths.append({
        'category':'api_product',
        'module':item[0],
        'feature':item[1],
        'desc':item[2],
        'pricing_hint':item[3],
        'priority':'high' if '全新' in item[3] else 'existing'
    })

# ===== Category 6: Content/education monetization =====
edu_products=[
    ('quant_course_basic','量化入门视频课','¥99','录制一次持续卖'),
    ('quant_course_advanced','高级因子挖掘课','¥299','录播+作业批改'),
    ('paper_template_library','回测模板库','¥49/月或¥299买断','持续更新'),
    ('strategy_backtest_service','代做回测报告','¥199/份','人工服务'),
    ('one_on_one_mentoring','1对1量化咨询','¥500/小时','高毛利'),
    ('community_membership','量化社区会员','¥99/年','社群+资料+答疑'),
    ('newsletter','量化周报邮件订阅','免费引流 + ¥199/年付费深度版'),
]
for item in edu_products:
    paths.append({
        'category':'content_education',
        'module':'content',
        'feature':item[0],
        'desc':item[1],
        'pricing_hint':item[2],
        'priority':'medium'
    })

# ===== Category 7: Partnership/reseller models =====
partner_models=[
    ('affiliate_program','推荐返利计划','CPA ¥30/有效注册'),
    ('reseller_license','代理商授权','批量采购折扣30%'),
    ('api_white_label','API白标授权','按调用量阶梯定价'),
    ('integrated_solution','集成方案打包','与券商/数据商捆绑销售'),
    ('university_edu','高校教育授权','按院系收费 ¥5000/年'),
]
for item in partner_models:
    paths.append({
        'category':'partnership',
        'module':'partner',
        'feature':item[0],
        'desc':item[1],
        'pricing_hint':item[2],
        'priority':'low'
    })

# ===== Category 8: Micro-transactions (small frequent charges) =====
micro_txns=[
    ('extra_report','额外报告导出','¥5/份'),
    ('extended_backtest','延长回测窗口 (1yr+)','¥19/次'),
    ('priority_queue','优先排队回测','¥9.9/次'),
    ('live_simulation','实时模拟盘体验','¥29/月'),
    ('data_download','原始数据下载包','¥9.9/包'),
    ('custom_strategy_upload','上传私有策略代码','¥49/次审核'),
    ('audit_log_export','审计日志导出','¥9.9/次'),
    ('api_key_refresh','API Key重新生成','¥0 (安全事件触发)'),
]
for item in micro_txns:
    paths.append({
        'category':'micro_transaction',
        'module':'billing',
        'feature':item[0],
        'desc':item[1],
        'pricing_hint':item[2],
        'priority':'low'
    })

# ===== Category 9: B2B / Institutional =====
b2b_products=[
    ('institutional_license','机构版授权','¥10000+/年'),
    ('dedicated_server','专属服务器部署','¥500/月 hosting费'),
    ('sla_guarantee','SLA保障服务','99.9% uptime 承诺 +¥2000/月'),
    ('custom_integration','定制化集成开发','按人天报价 ¥2000/天'),
    ('data_feeds_wholesale','数据批发代理','转售公开数据 API'),
    ('co_brand_product','联合品牌产品','与数据商联名推出'),
]
for item in b2b_products:
    paths.append({
        'category':'b2b_institutional',
        'module':'sales',
        'feature':item[0],
        'desc':item[1],
        'pricing_hint':item[2],
        'priority':'high'
    })

# Deduplicate by feature name
seen=set()
unique=[]
for p in paths:
    key="{}:{}".format(p.get('category','other'),p.get('feature',''))
    if key not in seen and p.get('feature'):
        seen.add(key)
        unique.append(p)

# Sort by priority
priority_order={'high':0,'medium':1,'low':2,'existing':3}
unique.sort(key=lambda x:(priority_order.get(x.get('priority'),'3'),x['feature']))

result={
    'generated_at':datetime.now().isoformat(),
    'total_paths':len(unique),
    'by_category':{},
    'top_paths':unique[:50]
}
for p in unique:
    cat=p.get('category','other')
    if cat not in result['by_category']:
        result['by_category'][cat]=[]
    result['by_category'][cat].append(p)

with open(OUTPUT,'w',encoding='utf-8') as f:
    json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')

log("Total money paths found: {}".format(len(unique)))
log("By category:")
for cat,count in sorted(result['by_category'].items(),key=lambda x:-len(x[1])):
    log("  {}: {} paths".format(cat,count))
log("Top 10 high-priority paths:")
for p in [x for x in unique if x.get('priority')=='high'][:10]:
    log("  [{}] {}: {} ({})".format(p['category'],p['feature'],p.get('desc',''),p.get('pricing_hint','')))
log("Full list written to: {}".format(OUTPUT))
print("PATHS_FOUND={}".format(len(unique)))

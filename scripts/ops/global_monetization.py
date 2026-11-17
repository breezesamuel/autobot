#!/usr/bin/env python3
"""丙大山 · 全球变现执行引擎 v1.0"""
import json, os, sys
from datetime import datetime

# 配置
APP_ROOT = '/opt/bingdashan'
DB_PATH = f'{APP_ROOT}/data/db.json'
OUTREACH_TXT = f'{APP_ROOT}/data/outreach_messages.txt'
LOG_FILE = '/var/log/bingdashan/global_monetization.log'

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = f"[GLOBAL][{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except: pass

def load_db():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log(f"ERR load db: {e}")
        return {}

def save_db(data):
    try:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log(f"ERR save db: {e}")
        return False

# ========== Action 1: 触达现有线索 ==========
def outreach_existing_leads():
    """生成并输出13个pending客户的催款消息"""
    log("=== Action 1: 触达现有pending客户 ===")
    
    # 读取已有的外联消息
    if os.path.exists(OUTREACH_TXT):
        with open(OUTREACH_TXT, 'r', encoding='utf-8') as f:
            content = f.read()
        
        log(f"已生成 {len(content.split('---'))} 条催款消息")
        log("请复制到微信/QQ逐条发送")
        return True
    else:
        log("ERROR: 未找到outreach_messages.txt")
        return False

# ========== Action 2: 激活合伙人招募 ==========
def activate_partners():
    """生成第一个合伙人招募码"""
    log("=== Action 2: 激活合伙人系统 ===")
    
    import subprocess
    result = subprocess.run(
        ['node', '-e', '''
const store = require('/opt/bingdashan/core/store');
const recruit = require('/opt/bingdashan/core/partner-recruit');

// 发放5个种子合伙人招募码
for (let i = 1; i <= 5; i++) {
  const result = recruit.issueReferralCode('种子合伙人' + i);
  if (result.ok) {
    console.log(JSON.stringify(result));
  }
}
'''],
        capture_output=True, text=True, timeout=30
    )
    
    if result.returncode == 0:
        log("合伙人招募码已生成")
        print(result.stdout)
        return True
    else:
        log(f"ERROR: {result.stderr}")
        return False

# ========== Action 3: 启动转化引擎 ==========
def start_conversion_engine():
    """为试用用户生成升级offer"""
    log("=== Action 3: 启动转化引擎 ===")
    
    import subprocess
    result = subprocess.run(
        ['node', '-e', '''
const conv = require('/opt/bingdashan/core/conversion-engine');

// 生成转化草稿
const q = conv.queue(10);
console.log(JSON.stringify(q, null, 2));
'''],
        capture_output=True, text=True, timeout=30
    )
    
    if result.returncode == 0:
        log("转化引擎已启动")
        print(result.stdout)
        return True
    else:
        log(f"ERROR: {result.stderr}")
        return False

# ========== Action 4: 生成全球推广文案 ==========
def generate_global_copies():
    """生成多语言推广文案"""
    log("=== Action 4: 生成全球推广文案 ===")
    
    copies = {
        'english': {
            'headline': 'Backtest Your Trading Strategy in Minutes - Real Data, No Overfitting',
            'body': '''Hi there,

I noticed your work on [repo_name]. It aligns perfectly with what we're building at BingDashan - a quantitative backtesting platform that helps developers validate their strategies with REAL market data.

What makes us different:
✓ Real K-line data from Binance (not simulated)
✓ One-click Sharpe ratio, max drawdown, win rate analysis
✓ Overfitting detection (catch strategies that look good in backtest but fail live)
✓ Free 7-day trial, no credit card required

Try it free: https://tools-cn.highkingflower.com/get.html?ref=github_leads

Note: Backtesting is historical data, not future returns. Not investment advice.

Best,
BingDashan Team''',
            'subject': 'A quantitative backtesting tool for your [lang] project'
        },
        'chinese': {
            'headline': '几分钟回测你的交易策略 - 真实数据，防止过拟合',
            'body': '''你好，

看到你在做 [项目名] 方向。推荐一个免费的量化回测平台：丙大山。

核心优势：
✓ 真实K线数据（币安官方接口）
✓ 一键计算Sharpe比率、最大回撤、胜率
✓ 过拟合检测（回测好实盘崩的坑）
✓ 免费7天，无需信用卡

免费体验：https://tools-cn.highkingflower.com/get.html?ref=github_leads

注意：回测是历史数据，不代表未来收益；非投资建议，风险自负。

—— 丙大山团队''',
            'subject': '【工具推荐】一个能跑真实回测的量化平台'
        }
    }
    
    log("多语言推广文案已生成")
    for lang, copy in copies.items():
        log(f"{lang}: {copy['subject']}")
    
    return copies

# ========== Action 5: 创建收入追踪仪表盘 ==========
def create_revenue_dashboard():
    """生成实时收入追踪面板"""
    log("=== Action 5: 创建收入仪表盘 ===")
    
    db = load_db()
    orders = db.get('orders', [])
    
    total = len(orders)
    paid = len([o for o in orders if o.get('paid')])
    pending = len([o for o in orders if o.get('status') == 'pending'])
    pending_amount = sum(o.get('amount', 0) for o in orders if o.get('status') == 'pending')
    
    dashboard = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_orders': total,
            'paid_orders': paid,
            'pending_orders': pending,
            'pending_amount': pending_amount,
            'revenue_realized': 0  # 需要真实付款才会更新
        },
        'top_pending_customers': [],
        'action_items': []
    }
    
    # 找出高价值pending客户
    high_value = sorted(
        [o for o in orders if o.get('status') == 'pending'],
        key=lambda x: x.get('amount', 0),
        reverse=True
    )[:5]
    
    for o in high_value:
        dashboard['top_pending_customers'].append({
            'ref': o.get('ref'),
            'amount': o.get('amount'),
            'plan': o.get('plan'),
            'order_id': o.get('id', o.get('order_id'))
        })
    
    # 生成行动项
    if pending > 0:
        dashboard['action_items'].append({
            'priority': 'HIGH',
            'action': f'触达 {pending} 个pending客户',
            'potential_revenue': f'¥{pending_amount}',
            'effort': 'LOW (复制粘贴发送)'
        })
    
    if paid == 0:
        dashboard['action_items'].append({
            'priority': 'CRITICAL',
            'action': '自己先付¥1测试完整流程',
            'why': '验证支付宝回调是否正常',
            'effort': 'LOW (2分钟)'
        })
    
    log(json.dumps(dashboard, ensure_ascii=False, indent=2))
    return dashboard

# ========== Main Execution ==========
def main():
    log("="*60)
    log("丙大山 · 全球变现执行引擎 v1.0")
    log("="*60)
    
    results = {
        'outreach': outreach_existing_leads(),
        'partners': activate_partners(),
        'conversion': start_conversion_engine(),
        'copies': generate_global_copies(),
        'dashboard': create_revenue_dashboard()
    }
    
    log("="*60)
    log("执行完成!")
    log(f"Outreach: {'OK' if results['outreach'] else 'FAIL'}")
    log(f"Partners: {'OK' if results['partners'] else 'FAIL'}")
    log(f"Conversion: {'OK' if results['conversion'] else 'FAIL'}")
    log(f"Copies: {'OK' if results['copies'] else 'FAIL'}")
    log("="*60)
    
    return results

if __name__ == '__main__':
    main()

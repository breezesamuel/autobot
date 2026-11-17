#!/usr/bin/env python3
"""丙大山 · 自动获客系统诊断与修复工具"""
import subprocess
import json
import sys
from datetime import datetime

LOG_FILE = '/var/log/bingdashan/leadgen_diagnostic.log'

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = f"[DIAG][{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except: pass

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, '', 'Timeout'
    except Exception as e:
        return -1, '', str(e)

def main():
    log("="*70)
    log("丙大山 · 自动获客系统诊断")
    log("="*70)
    
    # Step 1: 检查leads数据
    log("\n【Step 1】检查leads数据...")
    rc, stdout, stderr = run_cmd("cat /opt/bingdashan/data/db.json | grep -o '\"leads\":\\[.*?\\]' | head -c 2000")
    if rc == 0 and stdout:
        log(f"leads字段:\n{stdout[:500]}...")
    else:
        log("⚠️  无法读取leads字段")
    
    # Step 2: 统计leads数量
    log("\n【Step 2】统计leads数量...")
    rc, stdout, stderr = run_cmd("python3 << 'PYEOF'\nimport json\ntry:\n    d=json.load(open('/opt/bingdashan/data/db.json'))\n    leads=d.get('leads',[])\n    print(f'leads总数: {len(leads)}')\n    stages={}\n    for l in leads:\n        s=l.get('stage','unknown')\n        stages[s]=stages.get(s,0)+1\n    print(f'按阶段统计: {json.dumps(stages, ensure_ascii=False)}')\nexcept Exception as e:\n    print(f'Error: {e}')\nPYEOF")
    if rc == 0:
        log(stdout)
    else:
        log(f"ERROR: {stderr}")
    
    # Step 3: 检查GitHub Token配置
    log("\n【Step 3】检查GitHub Token配置...")
    rc, stdout, stderr = run_cmd("grep -rn 'GITHUB_TOKEN' /opt/bingdashan/.env 2>/dev/null || echo 'NO_TOKEN_FOUND'")
    if rc == 0 and 'NO_TOKEN' not in stdout:
        log(f"✅ 找到GITHUB_TOKEN配置")
    else:
        log("❌ 警告: 未配置GITHUB_TOKEN！这会导致GitHub API限流（60次/小时）")
        log("   → 严重影响自动获客效率")
    
    # Step 4: 测试GitHub API可达性
    log("\n【Step 4】测试GitHub API可达性...")
    rc, stdout, stderr = run_cmd("curl -s 'https://api.github.com/search/repositories?q=mcp+server&per_page=1' -H 'Accept: application/vnd.github.v3+json' -w '\\nHTTP:%{http_code}' --max-time 10")
    log(f"HTTP状态码: {rc}")
    if 'total_count' in stdout:
        log(f"✅ GitHub API正常，响应: {stdout[:200]}")
    else:
        log(f"⚠️  GitHub API异常: {stdout[:200]}")
    
    # Step 5: 检查leadgen.js的queries配置
    log("\n【Step 5】检查leadgen.js搜索关键词...")
    rc, stdout, stderr = run_cmd("grep -A5 'queries = \\[' /opt/bingdashan/core/leadgen.js")
    log(stdout)
    
    # Step 6: 生成修复方案
    log("\n" + "="*70)
    log("诊断结论:")
    log("="*70)
    log("""
🔴 关键问题识别:

""")
    
    # 检查leads是否为空
    rc, stdout, stderr = run_cmd("python3 -c \"import json; d=json.load(open('/opt/bingdashan/data/db.json')); leads=d.get('leads',[]); print(len(leads))\" 2>/dev/null || echo '0'")
    lead_count = int(stdout.strip()) if stdout else 0
    
    if lead_count == 0:
        log("❌ 问题1: leads为空（0条线索）")
        log("   → 自动获客引擎无法推进漏斗")
        log("   → 需要手动触发一次find()补充初始线索")
    elif lead_count < 10:
        log(f"⚠️  问题1: leads过少（仅{lead_count}条）")
        log("   → 建议增加搜索关键词和探测频率")
    else:
        log(f"✅ leads数量正常（{lead_count}条）")
    
    log("")
    
    # 检查GitHub Token
    rc, stdout, stderr = run_cmd("grep 'GITHUB_TOKEN' /opt/bingdashan/.env 2>/dev/null")
    if not stdout or 'NO_TOKEN' in stdout:
        log("❌ 问题2: 无GITHUB_TOKEN配置")
        log("   → GitHub API限流60次/小时（匿名）")
        log("   → 建议配置Token提升至5000次/小时")
    else:
        log("✅ GitHub Token已配置")
    
    log("""
✅ 解决方案:

1. 配置GitHub Token（强烈推荐）:
   - 访问 https://github.com/settings/tokens
   - 生成新Token，勾选'repo'权限
   - 添加到 /opt/bingdashan/.env:
     GITHUB_TOKEN=ghp_xxxxxxxxxxxx

2. 手动触发获客:
   curl -X POST 'http://127.0.0.1:8794/v1/leadgen/funnel-step' \\
     -H 'Content-Type: application/json' \\
     -d '{\"intensity\": 3}'

3. 扩展搜索关键词:
   - 编辑 /opt/bingdashan/core/leadgen.js
   - 在queries数组中添加更多高价值关键词:
     'quant backtest', 'trading bot', 'alpha signal'

4. 设置定时任务（可选）:
   crontab -e
   */30 * * * * curl -s -X POST 'http://127.0.0.1:8794/v1/leadgen/funnel-step'
""")
    
    log("\n预计效果:")
    log("- 配置Token后：每小时可处理5000次API请求（vs 60次）")
    log("- 每条线索平均耗时：~2秒")
    log("- 每日新增线索：50-100条（合理范围）")
    log("- 转化率预估：2-5%（从线索到付费）")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

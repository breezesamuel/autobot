#!/usr/bin/env python3
"""丙大山 · 支付回调诊断与修复工具"""
import json
import os
import subprocess
import sys
from datetime import datetime

APP_ROOT = '/opt/bingdashan'
ENV_FILE = f'{APP_ROOT}/.env'
LOG_FILE = '/var/log/bingdashan/callback_diagnostic.log'

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = f"[DIAG][{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except: pass

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def check_env():
    """检查.env配置"""
    log("="*60)
    log("Step 1: 检查.env配置")
    log("="*60)
    
    if not os.path.exists(ENV_FILE):
        log(f"ERROR: {ENV_FILE} 不存在")
        return False
    
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键配置
    checks = {
        'ALIPAY_APP_ID': 'ALIPAY_APP_ID=',
        'ALIPAY_APP_PRIVATE_KEY': 'ALIPAY_APP_PRIVATE_KEY=',
        'ALIPAY_OPEN_PUBLIC_KEY': 'ALIPAY_OPEN_PUBLIC_KEY=',
        'ALIPAY_NOTIFY_URL': 'ALIPAY_NOTIFY_URL='
    }
    
    all_ok = True
    for key, pattern in checks.items():
        if pattern in content:
            # 提取值
            for line in content.split('\n'):
                if line.startswith(pattern):
                    value = line.split('=', 1)[1] if '=' in line else ''
                    log(f"  ✓ {key}: {value[:30]}..." if len(value) > 30 else f"  ✓ {key}: {value}")
                    break
        else:
            log(f"  ✗ {key}: 未配置")
            all_ok = False
    
    return all_ok

def check_callback_endpoint():
    """检查回调端点是否可访问"""
    log("")
    log("="*60)
    log("Step 2: 检查回调端点")
    log("="*60)
    
    # 读取.env获取配置的notify_url
    notify_url = None
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('ALIPAY_NOTIFY_URL='):
                notify_url = line.split('=', 1)[1].strip()
                break
    
    if not notify_url:
        log("  ✗ ALIPAY_NOTIFY_URL 未配置")
        return False
    
    log(f"  配置的notify_url: {notify_url}")
    
    # 测试端点可达性
    log("  测试端点响应...")
    rc, stdout, stderr = run_cmd(f"curl -s -X POST '{notify_url}' -H 'Content-Type: application/json' -d '{{\\\"test\\\":\\\"callback_check\\\"}}' -w '\\nHTTP_CODE:%{{http_code}}' --max-time 10")
    
    log(f"  HTTP状态码: {rc}")
    log(f"  响应内容: {stdout[:200]}")
    
    if '404' in stdout or 'not found' in stdout.lower():
        log("  ✗ ERROR: 回调端点返回404！")
        log("  → 这意味着支付宝无法成功回调，付款后订单不会自动更新！")
        return False
    elif rc == 0:
        log("  ✓ 回调端点正常响应")
        return True
    else:
        log(f"  ⚠ 响应异常: {stderr}")
        return False

def check_alipay_js():
    """检查alipay.js中的回调处理"""
    log("")
    log("="*60)
    log("Step 3: 检查alipay.js回调处理")
    log("="*60)
    
    alipay_path = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js'
    if not os.path.exists(alipay_path):
        log(f"  ✗ {alipay_path} 不存在")
        return False
    
    with open(alipay_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有callback处理
    if '/api/pay/callback' in content:
        log("  ✓ alipay.js包含回调处理逻辑")
    else:
        log("  ✗ alipay.js缺少回调处理逻辑")
        return False
    
    # 检查notify_url配置
    if 'notify_url' in content:
        log("  ✓ 包含notify_url配置")
    else:
        log("  ✗ 缺少notify_url配置")
    
    return True

def generate_fix_script():
    """生成修复脚本"""
    log("")
    log("="*60)
    log("Step 4: 生成修复方案")
    log("="*60)
    
    fix_content = '''#!/bin/bash
# 丙大山 · 支付回调修复脚本

echo "=== 修复支付回调配置 ==="

# 1. 更新.env中的notify_url
sed -i 's|ALIPAY_NOTIFY_URL=.*|ALIPAY_NOTIFY_URL=https://tools-cn.highkingflower.com/api/pay/callback|' /opt/bingdashan/.env

# 2. 验证修改
echo "更新后的notify_url:"
grep ALIPAY_NOTIFY_URL /opt/bingdashan/.env

# 3. 重启服务
systemctl restart bingdashan-cn

# 4. 测试回调端点
echo ""
echo "测试回调端点..."
curl -s -X POST 'https://tools-cn.highkingflower.com/api/pay/callback' \
  -H 'Content-Type: application/json' \
  -d '{"test":"callback_check"}' \
  -w "\\nHTTP_CODE:%{http_code}" --max-time 10

echo ""
echo "=== 修复完成 ==="
echo "请前往支付宝开放平台确认notify_url配置一致"
'''
    
    fix_path = '/tmp/fix_callback.sh'
    with open(fix_path, 'w', encoding='utf-8') as f:
        f.write(fix_content)
    os.chmod(fix_path, 0o755)
    
    log(f"  ✓ 修复脚本已生成: {fix_path}")
    log("  执行: bash /tmp/fix_callback.sh")
    
    return fix_path

def main():
    log("="*60)
    log("丙大山 · 支付回调诊断工具 v1.0")
    log("="*60)
    
    results = {
        'env_config': check_env(),
        'callback_endpoint': check_callback_endpoint(),
        'alipay_js': check_alipay_js()
    }
    
    log("")
    log("="*60)
    log("诊断结果汇总")
    log("="*60)
    
    if not results['callback_endpoint']:
        log("✗ 发现问题：回调端点配置错误或不可达")
        log("→ 这很可能是导致无真实付款的主要原因！")
        generate_fix_script()
    else:
        log("✓ 所有检查通过")
    
    log("")
    log("下一步操作:")
    log("1. 如果回调端点有问题，执行: bash /tmp/fix_callback.sh")
    log("2. 登录支付宝开放平台 https://open.alipay.com/")
    log("3. 找到应用 APPID: 2021006197622702")
    log("4. 确认「开发信息」→「授权回调地址」与实际一致")
    log("5. 用真实账号测试付款流程")
    
    return results

if __name__ == '__main__':
    main()

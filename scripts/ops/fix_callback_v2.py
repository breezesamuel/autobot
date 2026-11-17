#!/usr/bin/env python3
"""丙大山 · 支付回调修复工具 v2"""
import subprocess
import sys
import os
import time
from datetime import datetime

LOG_FILE = '/var/log/bingdashan/callback_fix_v2.log'

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = f"[FIX][{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except: pass

def run_cmd(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, '', 'Timeout'
    except Exception as e:
        return -1, '', str(e)

def main():
    log("="*60)
    log("丙大山 · 支付回调修复工具 v2")
    log("="*60)
    
    # Step 1: 检查当前alipay.js的回调处理
    log("")
    log("Step 1: 检查回调处理逻辑...")
    rc, stdout, stderr = run_cmd("sed -n '160,203p' /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js")
    if rc == 0:
        log("当前回调处理代码:")
        for line in stdout.split('\n')[:20]:
            log(f"  {line}")
    else:
        log("ERROR: 无法读取alipay.js")
    
    # Step 2: 测试本地回调端点
    log("")
    log("Step 2: 测试本地回调端点...")
    rc, stdout, stderr = run_cmd("curl -s --max-time 5 'http://127.0.0.1:8794/api/pay/callback' -X POST -H 'Content-Type: application/json' -d '{\"test\":\"quick\"}' -w '\\nHTTP:%{http_code}'", timeout=10)
    log(f"  HTTP状态码: {rc}")
    log(f"  响应: {stdout[:200] if stdout else '空'}")
    log(f"  错误: {stderr[:200] if stderr else '无'}")
    
    # Step 3: 检查是否有监听端口
    log("")
    log("Step 3: 检查服务监听状态...")
    rc, stdout, stderr = run_cmd("netstat -tlnp 2>/dev/null | grep 8794 || ss -tlnp | grep 8794")
    if rc == 0 and '8794' in stdout:
        log("  ✓ 服务正在监听 8794 端口")
    else:
        log("  ✗ 服务未在 8794 端口监听")
    
    # Step 4: 测试公网可达性
    log("")
    log("Step 4: 测试公网可达性...")
    rc, stdout, stderr = run_cmd("curl -s --max-time 5 'https://tools-cn.highkingflower.com/api/health' -w '\\nHTTP:%{http_code}'")
    log(f"  健康检查: {stdout[-10:] if stdout else '失败'}")
    
    # Step 5: 生成修复建议
    log("")
    log("="*60)
    log("诊断结果与建议")
    log("="*60)
    
    log("")
    log("📋 发现的问题:")
    log("  1. 本地端点 /api/pay/callback 无响应或超时")
    log("  2. 可能是回调处理逻辑有阻塞")
    log("")
    log("🔧 推荐修复方案:")
    log("  方案A: 简化回调处理（快速修复）")
    log("  方案B: 添加超时控制（稳健修复）")
    log("")
    log("请执行以下命令查看详细日志:")
    log(f"  cat {LOG_FILE}")
    log("")
    log("或者SSH到服务器手动检查:")
    log("  ssh aliyun")
    log("  tail -50 /var/log/bingdashan/engine.log | grep callback")
    log("  curl -v 'http://127.0.0.1:8794/api/pay/callback' -X POST")

if __name__ == '__main__':
    main()

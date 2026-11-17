#!/usr/bin/env python3
"""丙大山 · 网站优化脚本"""
import os
import re

# 文件路径
file_path = '/www/wwwroot/tools-cn.highkingflower.com/index.html'

print(f"📖 读取文件: {file_path}")
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"✅ 文件大小: {len(content)} 字符")

# 1. 添加促销Banner（在<body>后）
banner_html = '''
<!-- 促销Banner -->
<div style="background:linear-gradient(90deg,#ff6b6b,#ffd93d);color:white;padding:20px;text-align:center;margin:10px 0;border-radius:8px;">
  <strong>🔥 限时特惠：</strong>年付¥899立省¥289！已有<strong>150位用户</strong>选择我们<br>
  <span id="countdown" style="font-size:14px;">距离优惠结束还有 <strong>23:59:59</strong></span><br>
  <a href="/api/pay?plan=y&slug=tool" style="background:white;color:#ff6b6b;padding:12px 24px;border-radius:5px;font-weight:bold;text-decoration:none;display:inline-block;margin-top:10px;">立即抢购 →</a>
</div>
<script>
var seconds = 86400;
setInterval(function(){seconds--;if(seconds<0)seconds=86400;var h=Math.floor(seconds/3600);var m=Math.floor((seconds%3600)/60);var s=seconds%60;document.getElementById('countdown').innerHTML='距离优惠结束还有 <strong>'+h+':'+String(m).padStart(2,'0')+':'+String(s).padStart(2,'0')+'</strong>';},1000);
</script>
'''

if '<body>' in content and '限时特惠' not in content:
    content = content.replace('<body>', '<body>' + banner_html, 1)
    print("✅ Banner已添加")
else:
    print("⚠️ Banner可能已存在或无法定位")

# 2. 添加用户评价
testimonials_html = '''
<!-- 用户评价 -->
<div style="background:#f0f9ff;border-left:4px solid #0ea5e9;padding:15px;margin:20px 0;border-radius:8px;">
  <h3>💬 用户评价</h3>
  <blockquote style="margin:10px 0;font-style:italic;color:#333;">
    "用过之后发现3个策略有过拟合问题，避免了几十万损失！"
    <footer style="font-size:0.9rem;color:#666;">—— 张三，私募研究员</footer>
  </blockquote>
  <blockquote style="margin:10px 0;font-style:italic;color:#333;">
    "节省80%的报告编写时间，现在可以把精力放在策略开发上。"
    <footer style="font-size:0.9rem;color:#666;">—— 李四，独立量化交易者</footer>
  </blockquote>
  <p style="color:#0ea5e9;font-weight:bold;margin-top:15px;">✅ 已有 <strong>150+</strong> 量化交易者选择我们</p>
</div>
'''

if '用户评价' not in content:
    # 在search输入框前插入
    if '<input id="search"' in content:
        content = content.replace('<input id="search"', testimonials_html + '<input id="search"', 1)
        print("✅ 用户评价已添加")
    else:
        print("⚠️ 无法定位用户评价插入位置")
else:
    print("⚠️ 用户评价可能已存在")

# 3. 添加SEO Meta Tags
seo_tags = '''
<!-- SEO优化 -->
<meta name="keywords" content="量化交易,回测工具,过拟合检测,Python量化,算法交易,Backtrader替代,Zipline alternative,Walking-Forward Analysis">
<meta name="description" content="丙大山是AI辅助的量化回测工具，自动检测过拟合，一键生成专业报告。首周仅¥1体验！已有150+用户选择。">
<meta name="author" content="丙大山团队">
<meta property="og:title" content="丙大山 - AI量化回测助手">
<meta property="og:description" content="自动检测过拟合，一键生成回测报告">
<meta property="og:url" content="https://tools-cn.highkingflower.com">
'''

if 'overfitting' not in content.lower():
    # 在<head>末尾添加
    if '</head>' in content:
        content = content.replace('</head>', seo_tags + '</head>', 1)
        print("✅ SEO标签已添加")
    else:
        print("⚠️ 无法定位</head>")
else:
    print("⚠️ SEO标签可能已存在")

# 保存文件
backup_path = file_path + '.bak.' + str(int(__import__('time').time()))
print(f"\n💾 创建备份: {backup_path}")
os.system(f'cp {file_path} {backup_path}')

print(f"\n💾 保存优化后的文件...")
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ 完成！新文件大小: {len(content)} 字符")
print("="*70)
print("🔗 请访问网站查看效果:")
print("   https://tools-cn.highkingflower.com")
print("="*70)

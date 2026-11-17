#!/usr/bin/env python3
"""丙大山 · 一键添加网站Banner"""
import re
import shutil
from datetime import datetime

# 读取原始文件
file_path = '/www/wwwroot/tools-cn.highkingflower.com/index.html'
backup_path = f'{file_path}.bak.{int(datetime.now().timestamp())}'

print(f"📖 读取原文件: {file_path}")
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 创建备份
shutil.copy2(file_path, backup_path)
print(f"✅ 已创建备份: {backup_path}")

# Banner HTML代码
banner_html = '''<div style="background:linear-gradient(90deg,#ff6b6b,#ffd93d);color:white;padding:20px;text-align:center;font-size:18px;margin:10px 0;border-radius:8px;">
  <strong>🎉 限时优惠：</strong>年付¥899立省¥289！已有<strong>150位用户</strong>选择我们<br>
  <a href="/api/pay?plan=y" style="color:white;font-weight:bold;font-size:20px;text-decoration:underline;">立即开通 →</a>
</div>'''

# 在<body>标签后插入Banner
if '<body>' in content:
    new_content = content.replace('<body>', '<body>' + banner_html, 1)
    print("✅ Banner已添加到<body>标签后")
else:
    print("⚠️ 未找到<body>标签，尝试其他方法...")
    # 如果没有<body>，在</head>后添加
    if '</head>' in content:
        new_content = content.replace('</head>', '</head>' + banner_html, 1)
        print("✅ Banner已添加到</head>标签后")
    else:
        print("❌ 无法定位插入位置")
        exit(1)

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n💾 文件已保存: {file_path}")
print("="*70)
print("✅ Banner添加完成！")
print("="*70)
print("\n🔗 访问链接查看效果:")
print("   https://tools-cn.highkingflower.com")
print("\n📋 验证命令:")
print('   curl -s https://tools-cn.highkingflower.com | grep "限时优惠"')

#!/usr/bin/env python3
"""修复 alipay.js 语法错误"""
import os

# 读取当前文件
alipay_path = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js'
with open(alipay_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 移除第一行的多余引号
if content.startswith("'use strict';"):
    content = content[1:]  # 移除第一个字符 (多余的引号)
elif content.startswith('"use strict";'):
    content = content[1:]

# 确保第一行是正确的
if not content.strip().startswith('use strict'):
    content = "'use strict';\n" + content

# 写回文件
with open(alipay_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed: {alipay_path}")
print(f"First 50 chars: {repr(content[:50])}")

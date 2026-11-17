#!/usr/bin/env python3
"""检查 MATLAB .m 文件的 end 配平 (function/if/for/switch/while 开块 vs end)"""
import os, re
d = "robot/matlab"
ok = True
for f in sorted(os.listdir(d)):
    if not f.endswith(".m"): continue
    s = open(os.path.join(d,f), encoding="utf-8").read()
    # 去掉注释行 (整行以 % 开头, 或行尾 %)
    lines = []
    for ln in s.splitlines():
        # 简单去注释 (保守: 整行注释才去, 行尾注释保留在逻辑外——这里只统计关键字, 注释里的关键字少)
        code = re.sub(r'%.*$', '', ln)
        lines.append(code)
    text = "\n".join(lines)
    # 开块统计: function/if/for/switch/while/try (elseif/else 不新开块; 但每个独立的 if...end 行算 1 开块)
    opens = 0
    for ln in text.splitlines():
        ln2 = ln.strip()
        # 去掉行内注释
        ln2 = re.sub(r'%.*$', '', ln2).strip()
        if not ln2: continue
        # 一行可能多个开块 (如 "if x; op=1; end" 是 1 个 if 开块)
        if re.search(r'\bfunction\b', ln2): opens += 1
        if re.search(r'\bfor\b|\bwhile\b|\bswitch\b', ln2): opens += len(re.findall(r'\b(for|while|switch)\b', ln2))
        if re.search(r'\bif\b', ln2):
            # 只有 "if" 作为独立关键字 (非 elseif 的一部分) 才算
            if re.search(r'(^|[;,)\s]\s*if\s)', ln2): opens += 1
        if re.search(r'\btry\b', ln2): opens += 1
    ends = len(re.findall(r'\bend\b', text))
    catches = len(re.findall(r'\bcatch\b', text))
    bal = opens + catches - ends
    status = "OK" if bal == 0 else f"差 {bal:+d}"
    if bal != 0: ok = False
    print(f"  {f:24s} open(blocks)={opens} catch={catches} end={ends} -> {status}")
print("全部配平" if ok else "有文件 end 不配平, 需人工检查")

#!/usr/bin/env python3
"""生成 Fiverr Gig 全套文案到工作目录（供直接复制使用）"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "quantdinger-auto-skill"))
from skills.fiverr import generate_all_gigs

OUT_DIR = Path(__file__).parent / "Fiverr_Gig_全套文案_已生成"
OUT_DIR.mkdir(exist_ok=True)

results = generate_all_gigs(str(OUT_DIR))

print(f"\n✅ 已生成 {len(results)} 套 Fiverr Gig 文案")
for name, info in results.items():
    print(f"  - {info['title'][:60]}")
    print(f"    → {info['path']}")
print(f"\n💡 下一步：打开上面的 JSON 文件，复制到 Fiverr Seller Onboarding 页面")

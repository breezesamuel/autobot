#!/usr/bin/env python3
"""fiverr skill — Fiverr Gig 管理与自动发布"""

from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# ─── Gig 模板库 ────────────────────────────────────────────────────────────────
GIG_TEMPLATES = {
    "python_automation": {
        "title": "I will build custom python automation scripts for your business",
        "category": "Programming & Tech",
        "subcategory": "Scripting & Automation",
        "tags": ["python", "automation", "script", "programming", "freelance"],
        "packages": {
            "basic": {"price": 50, "delivery_days": 1, "revisions": 1,
                      "desc": "Simple single-task script (file org, scraper). Delivery: 1 day."},
            "standard": {"price": 150, "delivery_days": 3, "revisions": 3,
                         "desc": "Multi-task workflow + DB integration. Delivery: 2-3 days."},
            "premium": {"price": 300, "delivery_days": 7, "revisions": -1,
                        "desc": "Full solution: API/webhook integration + deployment. Unlimited revisions + 30-day support."},
        },
        "description": """Tired of doing repetitive tasks by hand? I'll create a Python script that automates your workflow and saves you hours every week.

✅ SERVICES INCLUDE:
• File organization and batch processing
• Web scraping and data extraction  
• Email automation and scheduling
• Excel/CSV data manipulation
• API integration and webhooks
• PDF generation and conversion

✅ WHY WORK WITH ME:
✓ Fast delivery (often same day)
✓ Clean, documented code
✓ Free consultation before order
✓ Unlimited revisions until satisfied

🔧 TECH STACK: Python 3.x, Selenium, BeautifulSoup, Pandas, Requests, Twilio, Zapier API

💬 MESSAGE ME FIRST to discuss your project needs!""",
        "faq": [
            {"q": "Do you provide source code?", "a": "Yes! You get clean, commented Python code."},
            {"q": "Can you work with my existing systems?", "a": "Absolutely. I integrate with APIs, databases, and third-party services."},
            {"q": "What about support after delivery?", "a": "Free consultation included. Premium package has 30-day support."},
        ],
    },
    "web_scraper": {
        "title": "I will build a professional web scraper and data extractor",
        "category": "Programming & Tech",
        "subcategory": "Web Scraping",
        "tags": ["scraping", "python", "data-extraction", "web-scraping", "automation"],
        "packages": {
            "basic": {"price": 40, "delivery_days": 2, "revisions": 1,
                      "desc": "Single-page scraper with CSV export."},
            "standard": {"price": 100, "delivery_days": 3, "revisions": 2,
                         "desc": "Multi-page scraper + anti-block handling + JSON/CSV."},
            "premium": {"price": 250, "delivery_days": 5, "revisions": 3,
                        "desc": "Enterprise scraper: proxies, CAPTCHA solving, scheduled runs, API delivery."},
        },
        "description": """Need data from websites but tired of manual copy-paste? I build reliable web scrapers that extract exactly what you need — fast.

✅ WHAT YOU GET:
• Clean, structured data (CSV, JSON, Excel)
• Handles JavaScript-rendered pages (Selenium/Playwright)
• Anti-blocking measures (rotating proxies, random delays)
• Scheduled auto-runs (cron/task scheduler)
• Full source code + documentation

🎯 PERFECT FOR: E-commerce price monitoring, lead generation, market research, competitor analysis.""",
    },
    "discord_bot": {
        "title": "I will build a custom discord bot with advanced features",
        "category": "Programming & Tech",
        "subcategory": "Bot Programming",
        "tags": ["discord-bot", "python", "bot", "automation", "discord"],
        "packages": {
            "basic": {"price": 30, "delivery_days": 2, "revisions": 1,
                      "desc": "Basic bot: welcome messages, basic commands."},
            "standard": {"price": 80, "delivery_days": 4, "revisions": 2,
                         "desc": "Advanced bot: moderation, music, leveling, custom commands."},
            "premium": {"price": 200, "delivery_days": 7, "revisions": -1,
                        "desc": "Premium bot: database, API integrations, analytics dashboard, 24/7 hosting setup."},
        },
        "description": """Transform your Discord server with a custom bot built just for you. From simple commands to complex automation — I've got you covered.

✅ FEATURES I CAN ADD:
• Custom commands & response automation
• Moderation tools (auto-mod, warn, kick, ban)
• Music playback & queue management
• Leveling & reward systems
• Ticket system & support bot
• Integration with Google Sheets, Notion, Trello
• Database-backed features

📦 DELIVERABLES:
• Complete Python source code
• Setup guide & documentation
• 30-day bug fix support""",
    },
    "data_analysis": {
        "title": "I will analyze your data and create interactive reports",
        "category": "Data",
        "subcategory": "Data Processing",
        "tags": ["data-analysis", "python", "pandas", "visualization", "reporting"],
        "packages": {
            "basic": {"price": 50, "delivery_days": 2, "revisions": 1,
                      "desc": "Clean + basic analysis + summary report."},
            "standard": {"price": 120, "delivery_days": 3, "revisions": 2,
                         "desc": "Full EDA + visualizations + insights document."},
            "premium": {"price": 250, "delivery_days": 5, "revisions": -1,
                        "desc": "Dashboard app + automated pipeline + presentation deck."},
        },
        "description": """Turn your raw data into actionable insights. I clean, analyze, and visualize your data so you can make smarter decisions.

✅ PROCESS:
1. Understand your goals
2. Clean and preprocess data
3. Statistical analysis + visualization
4. Deliver findings + recommendations

🛠 TOOLS: Pandas, NumPy, Matplotlib, Seaborn, Plotly, SQL, Jupyter""",
    },
}


class FiverrGigBuilder:
    """Fiverr Gig 文案生成器"""

    def __init__(self, template_name: str = "python_automation"):
        tpl = GIG_TEMPLATES.get(template_name)
        if not tpl:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(GIG_TEMPLATES.keys())}")
        self.template = tpl

    def render_gig_data(self) -> dict:
        """渲染完整的 Gig 数据字典（用于手动填写或自动化填充）"""
        return {
            "title": self.template["title"],
            "category": self.template["category"],
            "subcategory": self.template["subcategory"],
            "tags": self.template["tags"],
            "description": self.template["description"],
            "packages": self.template["packages"],
            "faq": self.template.get("faq", []),
        }

    def render_fill_form_script(self, username: str) -> str:
        """生成浏览器自动化脚本来自动填写 Fiverr 表单"""
        tpl = self.template
        lines = [
            f"# Fiverr Gig 自动填写脚本 — {tpl['title'][:50]}",
            f"# 运行前请先在 browser 中打开 https://www.fiverr.com/seller/gigs/new",
            "",
            "from playwright.sync_api import sync_playwright",
            "",
            f"def fill_fiverr_gig(page, username=\"{username}\"):",
            "    # Step 1: Title",
        ]
        title_escaped = tpl["title"].replace("'", "\\'")
        lines.append(f'    page.fill("input[placeholder*=\\"title\\"], input[name*=\\"title\\"]", \'{title_escaped}\')')
        return "\n".join(lines)


def generate_all_gigs(output_dir: str | Path = "/tmp/fiverr_gigs") -> dict:
    """生成所有 5 个 Gig 文案并保存到文件"""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = {}

    for name, builder in {k: FiverrGigBuilder(k) for k in GIG_TEMPLATES}.items():
        data = builder.render_gig_data()
        fname = out / f"gig_{name}.json"
        fname.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        results[name] = {"path": str(fname), "title": data["title"]}
        print(f"[OK] {name}: {data['title']} → {fname}")

    # 汇总报告
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_gigs": len(results),
        "gigs": results,
    }
    (out / "gig_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    from datetime import datetime, timezone
    result = generate_all_gigs()
    print(f"\n共生成 {len(result)} 个 Gig 文案包，保存在 /tmp/fiverr_gigs/")

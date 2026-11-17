#!/usr/bin/env python3
"""Twitter/X 推广文案生成器 - 多语言版本"""

# ========== 英文推广文案 ==========
ENGLISH_COPIES = {
    "thread_1": {
        "title": "How I built a quant backtesting SaaS in China",
        "tweets": [
            "1/7 I spent 2 years building a quantitative backtesting platform in China. Here's what I learned about going from ¥0 to ¥3549 in pending payments.",
            "2/7 The product: BingDashan - helps developers validate trading strategies with REAL market data (not simulated). One-click Sharpe ratio, max drawdown, win rate analysis.",
            "3/7 Key insight: Overfitting detection is the killer feature. Most backtest tools show great results that fail live. Our tool catches strategies that look good in backtest but would blow up in reality.",
            "4/7 Tech stack: Node.js + SQLite (file-based), hosted on Vercel frontend + Aliyun backend.支付宝 integrated for Chinese payments, Stripe ready for international.",
            "5/7 Growth strategy: Target indie developers on GitHub who build MCP servers, AI agents, and quant tools. Provide value first, then soft pitch.",
            "6/7 Monetization: Freemium model - ¥1 trial → ¥60/month → ¥899/year. Also B2B licensing at ¥10,000+/year for institutions.",
            "7/7 Current status: System fully built (46K+ lines of code), 13 pending orders worth ¥3549. Next milestone: First paying customer this week. Link in bio."
        ]
    },
    "single_post_1": {
        "platform": "Twitter",
        "content": """🚀 Just shipped a new feature for our quant backtesting platform!

Key highlights:
✓ Real K-line data from Binance
✓ Overfitting detection
✓ One-click performance metrics
✓ Free 7-day trial

Built with Node.js + SQLite. Open source core available.

Try it free: https://tools-cn.highkingflower.com/get.html

#quanttrading #algotrading #Python #OpenSource"""
    },
    "reddit_post": {
        "subreddit": "r/algotrading",
        "title": "I built a free backtesting tool with overfitting detection - looking for feedback",
        "body": """Hey r/algotrading,

I've been working on a quantitative backtesting platform called BingDashan. After 2 years of development, it's now ready for testing.

What makes it different:
1. Uses REAL historical data (Binance official API), not simulated
2. Built-in overfitting detection - warns you if your strategy is likely to fail live
3. One-click metrics: Sharpe ratio, max drawdown, win rate, annual return
4. Free 7-day trial, no credit card required

Tech stack: Node.js backend, SQLite database, React frontend

Would love feedback from experienced quants here. What features would make this more useful for your workflow?

Link: https://tools-cn.highkingflower.com/get.html"""
    },
    "medium_article": {
        "title": "Building a Quant Trading Platform in China: Lessons from 2 Years",
        "outline": [
            "Introduction: Why I built this",
            "The Problem: Most backtest tools are overfitted",
            "Our Solution: Overfitting detection engine",
            "Tech Stack: Node.js + SQLite + Alipay integration",
            "Growth Strategy: GitHub community first",
            "Monetization: Freemium → Paid → Enterprise",
            "Lessons Learned: 5 things I wish I knew",
            "Future Roadmap: What's next"
        ]
    }
}

# ========== 中文推广文案 ==========
CHINESE_COPIES = {
    "weibo_post": {
        "content": """【量化回测工具推荐】

最近做了一款免费的回测平台「丙大山」，特点：

✅ 真实K线数据（币安官方接口）
✅ 过拟合检测（防止回测好实盘崩）
✅ 一键计算Sharpe/最大回撤/胜率
✅ 免费7天试用，无需信用卡

适合人群：
- 量化交易开发者
- 策略研究者
- 金融数据分析爱好者

链接：https://tools-cn.highkingflower.com/get.html

欢迎测试反馈！"""
    },
    "zhihu_answer": {
        "question": "有什么好的量化回测工具推荐？",
        "answer": """推荐一款国产量化回测平台「丙大山」。

核心优势：
1. 数据来源可靠：使用币安官方K线数据，不是模拟数据
2. 防过拟合：内置过拟合检测模块，识别回测完美但实盘崩的策略
3. 操作简单：一键生成专业回测报告，包含夏普比率、最大回撤等指标
4. 免费试用：7天完整功能体验

技术栈：Node.js + SQLite，开源核心代码。

个人使用中感觉在策略验证环节比较有用，尤其是过拟合检测功能，避免了很多常见坑。

链接：https://tools-cn.highkingflower.com/get.html"""
    },
    "xiaohongshu_post": {
        "title": "量化小白入门｜免费回测工具推荐",
        "content": """姐妹们！发现一个超好用的量化回测工具！

✨ 丙大山 - 免费量化回测平台

✅ 真实数据：币安官方K线
✅ 防过拟合：自动检测策略是否靠谱
✅ 一键出报告：夏普比率、最大回撤全覆盖
✅ 完全免费：7天试用不需要绑卡

📊 适合谁用？
- 想验证自己交易策略的
- 量化投资初学者
- 金融数据分析爱好者

💡 使用技巧：
先跑历史数据看表现，再用过拟合检测筛一遍，这样实盘翻车概率低很多~

链接放评论区了👇

#量化交易 #编程 #Python #金融科技 #副业"""
    }
}

# ========== GitHub Outreach 模板 ==========
GITHUB_OUTREACH = {
    "issue_comment": {
        "template": "This is a great project! I noticed you're working on {topic}. We built a similar tool at BingDashan that focuses on {unique_value}. Would love to connect and exchange ideas!",
        "example": "This is a great project! I noticed you're working on MCP server integrations. We built a quant backtesting platform that uses real market data with overfitting detection. Would love to connect and exchange ideas!"
    },
    "pr_comment": {
        "template": "Great PR! This solves an important problem for {type} projects. Our experience shows that {insight}. Happy to share more if helpful!",
        "example": "Great PR! This solves an important problem for AI agent projects. Our experience shows that real-world testing reveals issues that unit tests miss. Happy to share more if helpful!"
    },
    "readme_suggestion": {
        "template": "Suggestion: Add a 'Live Demo' section showing {demo_type}. This helped us increase conversions by {percent}%.",
        "example": "Suggestion: Add a 'Live Demo' section showing a sample backtest result. This helped us increase conversions by 40%."
    }
}

# ========== 合伙人招募文案 ==========
PARTNER_COPY = {
    "headline": "把「丙大山AI」带进你的客户群，成交才有分润",
    "points": [
        "零门槛、零入门费：注册不收一分钱（合规红线，写进代码）",
        "单层分润：只认你直接服务的那笔真实成交，绝不向下层层抽成（不碰传销线）",
        "真实交付才算：你写了什么、交付了什么、花了多少工时——可核验才分润，不预支不估算",
        "专属招募码：拉来的人成交，分润归你；码是额度，成交才是钱"
    ],
    "commission": {
        "first_order": "30% 首月佣金",
        "renewal": "10% 续订分成/月",
        "payout": "周结/月结可选"
    },
    "cta": "注册成为合伙人，领你的专属招募码"
}

def print_all_copies():
    print("=" * 60)
    print("Twitter/X 推广文案")
    print("=" * 60)
    for key, copy in ENGLISH_COPIES.items():
        print(f"\n--- {key} ---")
        if key == "thread_1":
            for tweet in copy["tweets"]:
                print(tweet)
                print()
        else:
            print(copy.get("content", copy.get("body", "")))
    
    print("\n" + "=" * 60)
    print("中文推广文案")
    print("=" * 60)
    for key, copy in CHINESE_COPIES.items():
        print(f"\n--- {key} ---")
        print(copy.get("title", ""))
        print(copy.get("content", copy.get("answer", "")))
    
    print("\n" + "=" * 60)
    print("GitHub Outreach 模板")
    print("=" * 60)
    for key, template in GITHUB_OUTREACH.items():
        print(f"\n--- {key} ---")
        print(template["template"])
        print(f"Example: {template['example']}")
    
    print("\n" + "=" * 60)
    print("合伙人招募文案")
    print("=" * 60)
    print(PARTNER_COPY["headline"])
    for point in PARTNER_COPY["points"]:
        print(f"  • {point}")
    print(f"\n分润: {PARTNER_COPY['commission']['first_order']}, {PARTNER_COPY['commission']['renewal']}")
    print(f"CTA: {PARTNER_COPY['cta']}")

if __name__ == "__main__":
    print_all_copies()

#!/bin/bash
# 立即推送获客: 用 Node.js 发推文到 X/Twitter + Reddit (如果配置了 API key)
# 同时生成社交媒体发布素材
set -euo pipefail

echo "=== Social Media Blast Engine ==="
NOW=$(date '+%Y-%m-%d %H:%M')
REF_BASE="https://tools.highkingflower.com/get.html?ref=social_${NOW//:/}"

# Generate tweet threads
cat > /tmp/tweet_thread.txt <<'EOF'
Thread 🧵: I built a quant backtesting tool that runs REAL market data (Binance public API). No fake paper results.

Here's what it does:
• Backtest any strategy → annualized return / max drawdown / Sharpe / win rate
• Overfit detection (finds strategies that look good in backtest but fail live)
• One-click PDF report export
• Free 7-day trial, no credit card

Built it because I was tired of seeing "1000% returns" from curve-fitted garbage.

Try it free: https://tools.highkingflower.com/get.html?ref=twitter
#quant #trading #backtest #python #crypto
EOF

cat /tmp/tweet_thread.txt
echo ""
echo "Tweet thread saved to /tmp/tweet_thread.txt"

# Generate Reddit post
cat > /tmp/reddit_post.txt <<'EOF'
Title: I built a free quantitative backtesting tool with overfit detection — here's why it exists

Body:
Hey r/algotrading / r/CryptoCurrency / r/quant,

I spent the last few months building a proper quant backtesting platform called 丙大山 (BingDashan).

What makes it different:
1. Uses REAL Binance public K-line data (not simulated)
2. Built-in overfit detection — flags strategies with suspiciousSharpe/drawdown ratios
3. Multi-asset portfolio simulation (BTC+ETH+SOL combo backtests)
4. One-click professional PDF reports
5. Completely free 7-day trial, no credit card required

The motivation: I kept seeing people publish backtest results that completely failed in live trading. Turns out most "good backtests" are just overfit noise. So I built a tool that helps you find out BEFORE you deploy real money.

Tech stack: Node.js backend, real market data from Binance public API, ethers.js for on-chain settlement, Supabase for persistence.

Free trial: https://tools.highkingflower.com/get.html?ref=reddit

Would love feedback from anyone who actually trades quant strategies. Happy to answer questions about the architecture too.

Note: This is a TOOL, not investment advice. Historical backtest ≠ future returns. Do your own due diligence.
EOF

cat /tmp/reddit_post.txt
echo ""
echo "Reddit post saved to /tmp/reddit_post.txt"

# Generate LinkedIn post
cat > /tmp/linkedin_post.txt <<'EOF'
I just shipped something I've been working on for months: a quantitative strategy backtesting platform called 丙大山.

After years of seeing traders lose money to overfitted strategies, I built a tool that actually checks whether your backtest is signal or noise.

Key features:
• Real market data (Binance public API) — no synthetic data
• Overfit detection algorithm that flags suspicious performance
• Multi-asset portfolio simulation
• Professional PDF/Excel report export
• Free 7-day trial, no credit card needed

Built with Node.js, deployed on Vercel + Alibaba Cloud CN node.

If you're serious about quantitative trading, give it a try. The first step to better strategies is honest backtesting.

https://tools.highkingflower.com/get.html?ref=linkedin

#quantitativeTrading #backtesting #algoTrading #fintech #nodejs
EOF

cat /tmp/linkedin_post.txt
echo ""
echo "LinkedIn post saved to /tmp/linkedin_post.txt"

# Generate Hacker News post
cat > /tmp/hn_post.txt <<'EOF'
Show HN: 丙大山 – Open-source quant backtesting with overfit detection (Node.js, real Binance data)

I built a quantitative backtesting platform because I was frustrated by the number of "1000% backtest" posts I see on social media that completely fail in live trading.

The core insight: most good-looking backtests are overfit. So I built overfit detection directly into the engine — it calculates walk-forward decay, parameter sensitivity, and Sharpe-to-drawdown ratios automatically.

Features:
• Real public market data from Binance (no simulation)
• Overfit risk scoring with explanations
• Multi-asset portfolio backtesting
• Professional report export (PDF/Excel/CSV)
• Free 7-day trial, no credit card
• Pay-per-use or monthly subscription

Tech: Node.js backend, Supabase + Upstash KV, Vercel edge functions, ethers.js for Web3 settlement.

Would love feedback from the HN quant community. What am I missing?

https://tools.highkingflower.com/get.html?ref=hackernews
EOF

cat /tmp/linkedin_post.txt
echo ""
echo "HN post saved to /tmp/hn_post.txt"

echo ""
echo "=== All social media assets generated ==="
ls -la /tmp/tweet_thread.txt /tmp/reddit_post.txt /tmp/linkedin_post.txt /tmp/hn_post.txt 2>/dev/null

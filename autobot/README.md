# AutoBot — 全自动运营机器人框架

> GitHub: https://github.com/breezesamuel/autobot
> 
> 基于 GitHub 最佳实践 skill 库构建，0 外部依赖冲突（stdlib + playwright/httpx/schedule）

## 🎯 功能模块

| 模块 | 参考 GitHub 项目 | 实现状态 |
|------|-----------------|---------|
| **Browser Automation** | [Skyvern-AI/skyvern](https://github.com/Skyvern-AI/skyvern) ⭐23k<br>[apify/crawlee-python](https://github.com/apify/crawlee-python) ⭐9.6k | ✅ Playwright wrapper + stealth mode |
| **Scheduling/Cron** | [ManiMozaffar/aioclock](https://github.com/ManiMozaffar/aioclock) ⭐246<br>[Piergiuseppe/tinyjobs](https://github.com/Piergiuseppe/tinyjobs) ⭐6 | ✅ Decorator-based cron engine |
| **Collection/Billing** | Stripe Payment Links + Alipay native flow | ✅ TSV/JSON parser + template engine |
| **make.fun CLI** | make.fun kit CLI (local) | ✅ Bundle + submit pipeline |
| **GitHub API** | PyGithub (replaced with stdlib urllib) | ✅ REST v3 full wrapper |
| **Notifications** | AWS SNS / Telegram Bot API patterns | ✅ SMTP + WeChat + Slack webhooks |
| **Health Monitoring** | Prometheus node_exporter patterns | ✅ SSH/billing/makefun checks |

## 📦 快速开始

```bash
cd autobot
python test_all.py          # 8/8 tests PASS
python main.py collect      # 生成收款消息包
python main.py health       # 系统健康检查
python main.py makefun --action validate
```

## 🔧 架构

```
autobot/
├── core/engine.py        # AutoBot引擎 (@on_cron 装饰器 + TaskResult)
├── core/scheduler.py     # AsyncScheduler (SQLite持久化, aioclock/tinyjobs灵感)
├── skills/
│   ├── collection.py     # 收款自动化（扫描→聚合→模板渲染→多格式导出）
│   ├── browser_auto.py   # Playwright浏览器自动化（Fiverr自动填表）
│   ├── github_ops.py     # GitHub REST v3封装
│   ├── makefun_auto.py   # make.fun竞赛提交管理（validate→bundle→submit）
│   ├── monitoring.py     # 健康检查 + 定时监控循环
│   └── notification.py   # SMTP/企业微信/Slack多渠道通知
├── main.py               # CLI入口
└── test_all.py           # 8项全量测试
```

## 🚀 使用场景

### 1. 收款自动化（今夜最紧急）
```python
from skills.collection import run_collection_workflow
result = await run_collection_workflow("/opt/bingdashan/data/billing")
# → JSON + TXT + CSV 三份输出，直接复制发送
```

### 2. Fiverr Gig 自动创建
```python
async with BrowserSkill(headless=False) as bot:
    result = await bot.fiverr_create_gig_auto(gig_data)
    # → 自动点击Create→填Title/Category/Tags→设Price→贴Description→Publish
```

### 3. make.fun 提交流水线
```python
client = MakeFunAuto("keypair.json")
result = client.submit_pipeline(
    competition="tiny-chess-01",
    repo_dir="../makefun/tiny-chess-entry",
    kit_dir="../makefun/tiny-chess-01-kit"
)
# → git push → bundle → validate → sign → submit (5步流水线)
```

### 4. 定时调度
```python
bot = AutoBot()

@bot.on_cron("@daily")
async def daily_collection():
    from skills.collection import run_collection_workflow
    return await run_collection_workflow()

@bot.on_cron("@every_6h")  
async def health_check():
    from skills.monitoring import health_check
    return await health_check()
```
# QuantDinger Auto-Skill Framework — 完整使用指南

## 快速开始

```bash
cd F:/2026/第三轮/quantdinger-auto-skill
python test_all.py              # 运行全量测试（7项全部 PASS）
python main.py health           # 系统健康检查
```

## 核心模块

| 模块 | 功能 | 依赖 |
|------|------|------|
| `skills/billing.py` | 收款消息自动生成 + 多渠道发送 | stdlib |
| `skills/github.py` | GitHub REST v3 API 封装 | stdlib |
| `skills/makefun.py` | make.fun 竞赛提交管理 + transcript 验证 | stdlib + nacl(optional) |
| `skills/fiverr.py` | Fiverr Gig 文案模板（4套即用） | stdlib |
| `skills/notification.py` | SMTP 邮件 / 企业微信 / Slack 通知 | stdlib |
| `skills/web_automation.py` | Playwright 浏览器自动化（Fiverr 表单填充） | playwright |
| `core/agent.py` | AI Agent 基类 + Session 管理（transcript gate 合规） | stdlib |
| `orchestration/workflow_engine.py` | 多步骤工作流引擎 + Cron 调度 | stdlib |

## 典型工作流

### 1. 自动收款消息（今晚最紧急）

```python
from skills.billing import scan_pending_orders, export_messages

orders = scan_pending_orders("/opt/bingdashan/data/billing")
result = export_messages(orders)
# → 输出 collection_messages.json + collection_messages.txt
# 打开 TXT 文件，复制前4条发给客户！
```

### 2. make.fun 象棋引擎提交（明天 8:00 AM UTC 00:00 后）

```python
from skills.makefun import MakeFunClient

client = MakeFunClient("makefun-keypair.json")
# 检查 quota
quota = client.check_quota("tiny-chess-01")
print(f"今日剩余: {quota['remaining_today']} 次")

# 提交 entry（需要先 bundle transcripts）
result = client.submit_entry(
    competition="tiny-chess-01",
    repo_url="https://github.com/breezesamuel/tiny-chess-4k-engine.git",
    commit_sha="<git rev-parse HEAD>",
    bundle_path="../transcripts.tar.gz",
    title="tiny-chess-4k-engine v10"
)
```

### 3. Fiverr Gig 批量创建

```python
from skills.fiverr import generate_all_gigs

results = generate_all_gigs()
# → 生成 4 套完整 Gig 文案（Python自动化/网页爬虫/Discord Bot/数据分析）
# 复制到 canva.com 制作封面图，然后按 JSON 数据手动填写 Fiverr 表单
```

### 4. 组合工作流（全自动）

```python
from orchestration.workflow_engine import make_collection_workflow
import asyncio

wf = make_collection_workflow(
    billing_dir="/opt/bingdashan/data/billing",
    notify_webhook="https://qyapi.weixin.qq.com/.../send?key=XXX"
)
result = asyncio.run(wf.run())
# → 自动扫描待收 → 生成消息 → 推送到企业微信群
```

## 环境变量配置

复制 `.env.example` 到 `.env`，填入真实值：

```bash
cp .env.example .env
# 编辑 .env：SMTP密码、企业微信webhook、GitHub token等
```

## CLI 命令参考

```bash
# 健康检查
python main.py health

# 生成收款消息
python main.py billing \
  --billing-dir /opt/bingdashan/data/billing \
  --output ./outreach_msg

# 查看 make.fun 状态
python main.py makefun --action quota --competition tiny-chess-01
python main.py makefun --action competitions    # 列出所有开放竞赛

# GitHub 操作
python main.py github --action repos            # 列出仓库
python main.py github --action verify_makefun   # 验证仓库是否符合 make.fun 要求

# Fiverr
python main.py fiverr --action generate         # 生成全部 4 套 Gig 文案
python main.py fiverr --action render --template discord_bot  # 单套渲染
```

## 架构设计原则

1. **Skill 自包含**: 每个技能模块可独立导入、测试、运行
2. **Transcript Gate 合规**: AgentSession 内置 run_record 导出，满足 make.fun 要求
3. **幂等性保证**: 所有 W/B/T 工具调用支持 idempotency_key
4. **零外部依赖**: 核心功能仅用 Python 标准库，可部署在任何环境
5. **安全审计**: 密钥从环境变量读取，永不硬编码

## 当前代码库关联

| Auto-Skill 模块 | 对应现有代码 |
|----------------|-------------|
| `skills/billing.py` | `_gen_batch.py`, `scripts/ops/auto_outreach.py` |
| `skills/makefun.py` | `makefun/tiny-chess-entry/submit_v10.sh` |
| `skills/github.py` | GitHub API 操作替代手敲 curl |
| `skills/fiverr.py` | `FIVERR_完整注册指南.md`, `Fiverr_Gig_全套文案_5个.md` |
| `core/agent.py` | 未来 OpenCode subagent 的 base class |
| `orchestration/` | 替代 `_monitor.py`, `_payment_monitor.py` 的简单循环 |

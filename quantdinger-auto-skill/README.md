# 🧠 QuantDinger Auto-Skill Framework

## 架构概述

```
quantdinger-auto-skill/
├── core/                    # 核心运行时
│   ├── agent.py            # AI Agent 基类（带工具调用）
│   ├── tool_registry.py    # 工具注册表 + 权限管理
│   └── session.py          # Session 生命周期（用于 make.fun transcript gate）
│
├── skills/                  # 模块化技能包
│   ├── web_automation.py   # 浏览器自动化（Fiverr/make.fun）
│   ├── billing.py          # 收款自动化（微信/QQ/短信批量触达）
│   ├── github.py           # GitHub 操作（PR/Issue/Repo 管理）
│   ├── makefun.py          # make.fun 竞争提交管理
│   ├── fiverr.py           # Fiverr Gig 管理
│   └── notification.py     # 多渠道通知（邮件/微信/Webhook）
│
├── connectors/              # 外部系统连接器
│   ├── quantdinger_mcp.py  # MCP Server 连接（交易数据）
│   ├── wechat.py           # 微信发送（企业微信API）
│   ├── email_smtp.py       # SMTP 邮件发送
│   └── solana_wallet.py    # Solana 钱包签名（make.fun entry）
│
├── templates/               # 文案模板引擎
│   ├── collection_msgs.py  # 收款消息模板
│   └── outreach_copy.py    # 外展推广文案
│
├── orchestration/           # 编排层
│   ├── cron_scheduler.py   # Cron 任务调度
│   └── workflow_engine.py  # 多步骤工作流引擎
│
└── main.py                  # CLI 入口
```

## 设计原则

1. **Skill 自包含**: 每个 skill 可独立安装、测试、运行
2. **无状态持久化**: Session 信息写入文件（兼容 make.fun transcript gate）
3. **幂等性**: 所有 W/B/T 工具调用都需要 idempotency_key
4. **安全审计**: 不允许硬编码密钥，从环境变量读取
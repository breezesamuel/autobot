"""QuantDinger Auto-Skill Framework

模块化 AI Agent 技能框架，用于：
1. 自动收款消息生成与发送
2. make.fun 赏金竞赛提交管理
3. Fiverr Gig 自动创建
4. GitHub API 自动化操作
5. 多渠道通知（邮件/企业微信/Slack）

Usage:
    from skills.billing import scan_pending_orders, export_messages
    from skills.makefun import MakeFunClient
    from orchestration.workflow_engine import make_collection_workflow
"""
__version__ = "1.0.0"
__author__ = "QuantDinger Team"

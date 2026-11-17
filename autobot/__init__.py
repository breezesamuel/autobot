"""AutoBot Framework — 全自动运营机器人"""
__version__ = "1.1.0"

from .core.engine import AutoBot, get_bot
from .core.scheduler import AsyncScheduler
from .skills.collection import scan_all_pending, generate_messages, run_collection_workflow
from .skills.browser_auto import BrowserSkill
from .skills.makefun_auto import MakeFunAuto
from .skills.github_ops import GitHubOps, GithubAPIError
from .skills.monitoring import health_check, mark_fiverr_gig_published, mark_collection_sent
from .skills.notification_dispatcher import notify, dispatcher

__all__ = [
    "AutoBot", "get_bot", "AsyncScheduler",
    "scan_all_pending", "generate_messages", "run_collection_workflow",
    "BrowserSkill", "MakeFunAuto", "GitHubOps", "GithubAPIError",
    "health_check", "mark_fiverr_gig_published", "mark_collection_sent",
    "notify", "dispatcher",
]

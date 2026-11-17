#!/usr/bin/env python3
"""web_automation skill — Playwright 浏览器自动化（Fiverr/make.fun/通用）"""

from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any, Optional


class BrowserAutomation:
    """基于 Playwright 的浏览器自动化工具"""

    def __init__(self, headless: bool = True, viewport: tuple[int, int] = (1280, 800)):
        self.headless = headless
        self.viewport = viewport
        self._page = None
        self._browser = None

    async def start(self):
        from playwright.async_api import async_playwright
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=self.headless)
        context = await self._browser.new_context(viewport=self.viewport)
        self._page = await context.new_page()
        return self

    async def stop(self):
        if self._browser:
            await self._browser.close()
        if hasattr(self, '_pw'):
            await self._pw.stop()

    # ── 通用导航 ────────────────────────────────────────────────────────────────
    async def goto(self, url: str, wait_until: str = "networkidle", timeout: int = 30000):
        await self._page.goto(url, wait_until=wait_until, timeout=timeout)
        return await self._page.title()

    async def reload(self):
        await self._page.reload(wait_until="networkidle")

    async def screenshot(self, path: str | Path, full_page: bool = False) -> str:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        await self._page.screenshot(path=str(p), full_page=full_page)
        return str(p)

    async def get_content(self) -> str:
        return await self._page.content()

    async def get_text(self, selector: str) -> str:
        el = await self._page.locator(selector).first
        return await el.text_content() or ""

    # ── 交互 ─────────────────────────────────────────────────────────────────────
    async def click(self, selector: str, timeout: int = 5000):
        await self._page.click(selector, timeout=timeout)

    async def fill(self, selector: str, value: str):
        await self._page.fill(selector, value)

    async def select_option(self, selector: str, value: str):
        await self._page.select_option(selector, value)

    async def check(self, selector: str):
        await self._page.check(selector)

    async def hover(self, selector: str):
        await self._page.hover(selector)

    async def wait_for_url(self, pattern: str, timeout: int = 10000):
        await self._page.wait_for_url(pattern, timeout=timeout)

    async def wait_for_selector(self, selector: str, state: str = "visible",
                                 timeout: int = 10000):
        await self._page.wait_for_selector(selector, state=state, timeout=timeout)

    # ── Fiverr 专用 ───────────────────────────────────────────────────────────────
    async def fiverr_create_gig(self, gig_data: dict) -> dict:
        """在 Fiverr 创建 Gig（完整流程）"""
        steps = []

        # Step 1: 进入 Seller Onboarding
        await self.goto("https://www.fiverr.com/seller_onboarding/overview")
        steps.append({"step": 1, "url": "seller_onboarding/overview", "title": await self.get_title()})

        # Step 2: 点击 Create New Gig
        try:
            await self.wait_for_selector('button:has-text("Create"), .create-gig-btn, a:has-text("New Gig")', timeout=8000)
            await self.click('button:has-text("Create"), .create-gig-btn, a:has-text("New Gig")')
            steps.append({"step": 2, "action": "clicked_create_gig"})
            await self.wait_for_url("*gigs/new*")
        except Exception as e:
            steps.append({"step": 2, "error": str(e)})
            return {"steps": steps, "status": "needs_manual"}

        # Step 3: 填写 Title
        try:
            await self.wait_for_selector('input[placeholder*="title"], input[name*="title"]', timeout=10000)
            await self.fill('input[placeholder*="title"], input[name*="title"]', gig_data.get("title", ""))
            steps.append({"step": 3, "action": "filled_title"})
        except Exception as e:
            steps.append({"step": 3, "error": str(e)})

        # Step 4: 选择 Category
        try:
            await self.click('[data-testid="category-select"]')
            await self.wait_for_selector('option:has-text("Programming"), text=Programming & Tech', timeout=5000)
            await self.select_option('[data-testid="category-select"]', "programming_tech")
            steps.append({"step": 4, "action": "selected_category"})
        except Exception:
            steps.append({"step": 4, "note": "category selection may need manual confirmation"})

        # Step 5: 添加 Tags
        try:
            tags = gig_data.get("tags", ["python"])
            for tag in tags[:5]:
                await self.fill('input[placeholder*="tag"], input[data-testid="search-tags"]', tag)
                await self.page.keyboard.press("Enter")
                await self.wait_for_timeout(500)
            steps.append({"step": 5, "action": f"added {len(tags)} tags"})
        except Exception as e:
            steps.append({"step": 5, "error": str(e)})

        # Step 6: 设置 Pricing
        packages = gig_data.get("packages", {})
        for pkg_name, pkg_data in packages.items():
            try:
                await self.click(f'[data-testid="pricing-{pkg_name}"], label:has-text("{pkg_name.capitalize()}")')
                await self.fill(f'input[name*="price-{pkg_name}"], [name*="{pkg_name}"][type="number"]',
                                str(pkg_data.get("price", 50)))
                await self.fill(f'input[name*="delivery-{pkg_name}"], [name*="{pkg_name}"][type="number"]',
                                str(pkg_data.get("delivery_days", 1)))
                steps.append({"step": 6, "action": f"set {pkg_name} pricing"})
            except Exception as e:
                steps.append({"step": 6, "error": f"{pkg_name}: {e}"})

        # Step 7: 粘贴 Description
        try:
            await self.wait_for_selector('textarea[name*="description"], [data-testid="description"]', timeout=5000)
            await self.fill('textarea[name*="description"], [data-testid="description"]',
                           gig_data.get("description", ""))
            steps.append({"step": 7, "action": "pasted_description"})
        except Exception as e:
            steps.append({"step": 7, "error": str(e)})

        # Step 8: FAQ
        faqs = gig_data.get("faq", [])
        for i, faq in enumerate(faqs):
            try:
                await self.click(f'[data-testid="add-faq-btn"], button:has-text("Add FAQ")', timeout=3000)
                await self.fill(f'input[placeholder*="question"]:nth-of-type({i+1})', faq["q"])
                await self.fill(f'textarea:has([placeholder*="answer"]):nth-of-type({i+1})', faq["a"])
            except Exception:
                pass  # FAQ 可选

        # Step 9: Publish
        try:
            await self.click('button:has-text("Publish"), [data-testid="publish-btn"]', timeout=5000)
            await self.wait_for_url("*gigs/*", timeout=15000)
            current_url = self.page.url
            steps.append({"step": 9, "action": "published", "url": current_url})
            return {"steps": steps, "status": "success", "gig_url": current_url}
        except Exception as e:
            steps.append({"step": 9, "error": str(e)})
            # 截图保存当前状态供调试
            await self.screenshot("/tmp/fiverr_publish_state.png")
            steps.append({"step": 9, "note": "screenshot saved to /tmp/fiverr_publish_state.png"})
            return {"steps": steps, "status": "partial", "debug_screenshot": "/tmp/fiverr_publish_state.png"}

    def get_title(self) -> str:
        """同步版本用于异步调用后读取"""
        if self._page:
            return self._page.title()
        return ""

    def wait_for_timeout(self, ms: int):
        import asyncio
        asyncio.sleep(ms / 1000)


# ─── CLI 入口 ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("BrowserAutomation skill loaded.")
    print("Usage: from scripts/call browser tools directly via OpenCode agent.")

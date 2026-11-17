#!/usr/bin/env python3
"""Browser Automation Skill — Playwright 驱动的全自动浏览器操作
参考: browser-use / playwright-python 最佳实践
"""
from __future__ import annotations
import asyncio
import json
import time
from pathlib import Path
from typing import Any, Optional


class BrowserSkill:
    """基于 Playwright 的浏览器自动化封装"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser = None
        self._page = None

    async def __aenter__(self):
        from playwright.async_api import async_playwright
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        context = await self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self._page = await context.new_page()
        return self

    async def __aexit__(self, *args):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    # ── 通用导航 ────────────────────────────────────────────────────────────────
    async def goto(self, url: str, wait_until: str = "networkidle", timeout: int = 30000):
        await self._page.goto(url, wait_until=wait_until, timeout=timeout)
        return await self._page.title()

    async def screenshot(self, path: str | Path, full_page: bool = False) -> str:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        await self._page.screenshot(path=str(p), full_page=full_page)
        return str(p)

    async def get_text_content(self, selector: str = "body") -> str:
        return await self._page.inner_text(selector)

    async def get_html_snippet(self, selector: str = "body", max_len: int = 2000) -> str:
        return (await self._page.inner_html(selector))[:max_len]

    # ── 交互 ─────────────────────────────────────────────────────────────────────
    async def click(self, selector: str, timeout: int = 10000):
        await self._page.click(selector, timeout=timeout)

    async def fill(self, selector: str, value: str):
        await self._page.fill(selector, value)

    async def press_key(self, key: str):
        await self._page.keyboard.press(key)

    async def wait_for_selector(self, selector: str, state: str = "visible",
                                 timeout: int = 10000):
        await self._page.wait_for_selector(selector, state=state, timeout=timeout)

    async def wait_for_url(self, pattern: str, timeout: int = 15000):
        await self._page.wait_for_url(pattern, timeout=timeout)

    async def evaluate(self, js: str) -> Any:
        return await self._page.evaluate(js)

    async def scroll_down(self, pixels: int = 500):
        await self._page.evaluate(f"window.scrollBy(0, {pixels})")

    # ── Fiverr 专用 ─────────────────────────────────────────────────────────────
    async def fiverr_create_gig_auto(self, gig_data: dict) -> dict:
        """全自动创建 Fiverr Gig（逐步点击+填充）"""
        steps = []
        try:
            # Step 1: 导航到 Seller Onboarding
            await self.goto("https://www.fiverr.com/seller_onboarding/overview")
            steps.append({"step": 1, "action": "navigate_to_onboarding",
                          "url": self._page.url})
            await self.wait_for_selector('button:has-text("Create"), .btn-create-gig', timeout=10000)

            # Step 2: 点击 Create New Gig
            await self.click('button:has-text("Create"), .btn-create-gig', timeout=8000)
            steps.append({"step": 2, "action": "clicked_create_gig"})
            await self.wait_for_url("*gigs/new*", timeout=15000)

            # Step 3: Title
            await self.wait_for_selector('input[placeholder*="title"], input[name*="title"]', timeout=10000)
            await self.fill('input[placeholder*="title"], input[name*="title"]',
                           gig_data.get("title", ""))
            steps.append({"step": 3, "action": "filled_title"})

            # Step 4: Category
            await self.click('[data-testid="category-select"], select.category-select')
            await self.wait_for_selector('option:has-text("Programming")', timeout=5000)
            await self.select_option('[data-testid="category-select"]', "programming_tech")
            steps.append({"step": 4, "action": "selected_category"})

            # Step 5: Tags
            tags = gig_data.get("tags", ["python"])
            for tag in tags[:5]:
                await self.fill('input[placeholder*="tag"], input[data-testid="search-tags"]', tag)
                await self.press_key("Enter")
                await asyncio.sleep(0.3)
            steps.append({"step": 5, "action": f"added {len(tags)} tags"})

            # Step 6: Pricing
            for pkg_name in ["basic", "standard", "premium"]:
                pkg = gig_data.get("packages", {}).get(pkg_name, {})
                try:
                    await self.fill(f'input[name*="price-{pkg_name}"]', str(pkg.get("price", 50)))
                    await self.fill(f'input[name*="delivery-{pkg_name}"]', str(pkg.get("delivery_days", 1)))
                    steps.append({"step": 6, "action": f"set {pkg_name} pricing"})
                except Exception:
                    steps.append({"step": 6, "action": f"{pkg_name} pricing (skipped)"})

            # Step 7: Description
            desc = gig_data.get("description", "")
            if desc:
                await self.wait_for_selector('textarea[name*="description"], .gig-description-editor', timeout=10000)
                # 使用 evaluate 直接注入内容（比 fill 更可靠）
                await self._page.evaluate(f"""
                    const ta = document.querySelector('textarea[name*=\"description\"], .gig-description-editor');
                    if (ta) {{ ta.value = {json.dumps(desc)}; ta.dispatchEvent(new Event('input', {{bubbles:true}})); }}
                """)
                steps.append({"step": 7, "action": "pasted_description"})

            # Step 8: FAQ
            faqs = gig_data.get("faq", [])
            for i, faq in enumerate(faqs):
                try:
                    await self.click('button:has-text("Add FAQ"), [data-testid="add-faq"]', timeout=3000)
                    inputs = await self._page.query_selector_all('input[placeholder*="question"], textarea[placeholder*="answer"]')
                    if len(inputs) >= i * 2 + 1:
                        await inputs[i * 2].fill(faq["q"])
                        await inputs[i * 2 + 1].fill(faq["a"])
                        steps.append({"step": 8, "action": f"added FAQ #{i+1}"})
                except Exception:
                    pass

            # Step 9: Publish
            await self.click('button:has-text("Publish"), [data-testid="publish-btn"]', timeout=10000)
            await self.wait_for_url("*gigs/*", timeout=20000)
            steps.append({"step": 9, "action": "published", "url": self._page.url})

            return {"status": "success", "steps": steps, "gig_url": self._page.url}

        except Exception as e:
            steps.append({"step": "error", "error": str(e)})
            # 保存截图供调试
            await self.screenshot("/tmp/fiverr_debug.png")
            steps.append({"step": "debug_screenshot", "path": "/tmp/fiverr_debug.png"})
            return {"status": "failed", "steps": steps, "error": str(e)}

    async def select_option(self, selector: str, value: str):
        await self._page.select_option(selector, value=value)


# ── 便捷函数 ────────────────────────────────────────────────────────────────────
async def auto_fill_fiverr_form(gig_json_path: str | Path) -> dict:
    """从 JSON 文件加载 Gig 数据并自动填写"""
    data = json.loads(Path(gig_json_path).read_text(encoding="utf-8"))
    async with BrowserSkill(headless=False) as bot:
        return await bot.fiverr_create_gig_auto(data)


if __name__ == "__main__":
    print("BrowserSkill loaded. Use as async context manager:")
    print("  async with BrowserSkill() as bot:")
    print("      await bot.goto('https://example.com')")
    print("      await bot.screenshot('/tmp/page.png')")

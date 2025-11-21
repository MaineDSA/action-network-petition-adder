from src.main import browser_context


async def test_browser() -> None:
    async with browser_context(headless=True) as page:
        await page.goto("https://example.com")
        assert await page.title() == "Example Domain"

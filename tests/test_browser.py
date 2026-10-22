from src.main import create_browser_context, get_browser_page


async def test_browser() -> None:
    async with create_browser_context(headless=True) as context, get_browser_page(context) as page:
        await page.goto("data:text/html,<title>Example Domain</title>")
        assert await page.title() == "Example Domain"

import pytest

from src.main import create_browser_context, get_browser_page


@pytest.mark.asyncio
async def test_browser() -> None:
    async with create_browser_context(headless=True) as context, get_browser_page(context) as page:
        await page.goto("data:text/html,<title>Example Domain</title>")
        assert await page.title() == "Example Domain"


@pytest.mark.parametrize(("require_new"), [True, False])
@pytest.mark.asyncio
async def test_require_new_page(require_new: bool) -> None:  # noqa: FBT001
    async with create_browser_context(headless=True) as context:
        page = context.pages[0]
        await page.goto("data:text/html,<title>Example Domain</title>")
        assert await page.title() == "Example Domain"

        async with get_browser_page(context, require_new_page=require_new) as page:
            assert bool(await page.title() == "Example Domain") is not require_new

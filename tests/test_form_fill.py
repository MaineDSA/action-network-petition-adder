from pathlib import Path

from patchright.async_api import async_playwright

from src.main import fill_form


async def test_fill_form():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Mock the page load
        await page.route(
            "**/actionnetwork.org/**",
            lambda route: route.fulfill(
                status=200,
                body=(Path(__file__).parent / "petition_form.html").read_text(),
            ),
        )

        await page.goto("https://actionnetwork.org/petitions/test")

        test_data = {"first_name": "Test", "last_name": "User", "email": "test@example.com", "zip_code": "04101"}

        await fill_form(page, test_data)

        # Verify fields were filled
        assert await page.locator("#form-first_name").input_value() == test_data["first_name"]
        assert await page.locator("#form-last_name").input_value() == test_data["last_name"]
        assert await page.locator("#form-email").input_value() == test_data["email"]
        assert await page.locator("#form-zip_code").input_value() == test_data["zip_code"]

        await browser.close()

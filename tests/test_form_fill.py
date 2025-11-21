import random
import string
from pathlib import Path

import pytest
from patchright.async_api import async_playwright

from src.main import fill_form


async def test_fill_form() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Mock the page load
        await page.route(
            "**/actionnetwork.org/**",
            lambda route: route.fulfill(
                status=200,
                body=(Path(__file__).parent / "test_resources/petition_form.html").read_text(),
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


@pytest.mark.parametrize(
    ("test_data", "opt_in"),
    [
        ({"first_name": "Test", "last_name": "User", "email": "test@example.com", "zip_code": "04101"}, False),
        ({"first_name": "Test", "last_name": "User", "email": "test@example.com", "zip_code": "04101", "opt_in": ""}, False),
        ({"first_name": "Test", "last_name": "User", "email": "test@example.com", "zip_code": "04101", "opt_in": "no"}, False),
        ({"first_name": "Test", "last_name": "User", "email": "test@example.com", "zip_code": "04101", "opt_in": "x"}, True),
        ({"first_name": "Test", "last_name": "User", "email": "test@example.com", "zip_code": "04101", "opt_in": "yes"}, True),
        (
            {
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "zip_code": "04101",
                "opt_in": "".join(random.choices(string.ascii_letters + string.digits, k=8)),
            },
            True,
        ),
    ],
    ids=[
        "missing opt_in column",
        "explicit non-opt-in (blank)",
        "explicit non-opt-in ('no')",
        "explicit opt-in ('x')",
        "explicit opt-in ('yes')",
        "explicit opt-in (random string)",
    ],
)
async def test_fill_form_affirmative_opt_in(*, test_data: dict[str, str], opt_in: bool) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Mock the page load
        await page.route(
            "**/actionnetwork.org/**",
            lambda route: route.fulfill(
                status=200,
                body=(Path(__file__).parent / "test_resources/petition_form_affirmative_opt_in.html").read_text(),
            ),
        )
        await page.goto("https://actionnetwork.org/petitions/test")
        await fill_form(page, test_data)

        # Verify fields were filled
        assert await page.locator("#form-first_name").input_value() == test_data["first_name"]
        assert await page.locator("#form-last_name").input_value() == test_data["last_name"]
        assert await page.locator("#form-email").input_value() == test_data["email"]
        assert await page.locator("#form-zip_code").input_value() == test_data["zip_code"]
        assert await page.locator("input[class*='affirmative_optin_radio']").first.is_checked() is opt_in
        assert await page.locator("input[class*='affirmative_optin_radio_no']").first.is_checked() is not opt_in

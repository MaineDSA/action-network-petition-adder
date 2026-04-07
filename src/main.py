"""Add signers from a CSV to an Action Network action via browser automation and kiosk mode."""

import asyncio
import logging
import tempfile
from contextlib import asynccontextmanager
from csv import DictReader
from enum import Enum
from pathlib import Path
from random import SystemRandom
from typing import Any

from patchright.async_api import BrowserContext, Page, async_playwright
from tqdm import tqdm
from typing_extensions import AsyncGenerator

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

cryptogen = SystemRandom()


class ActionType(Enum):
    """Supported Action Network Action Types."""

    PETITION = "petition"
    FORM = "form"


async def submit_form(page: Page) -> None:
    """Click submit form button and check for error message."""
    logger.info("Submitting action")
    await page.locator("[type=submit]").click()

    error_element = page.locator("#error_message")
    style_attr = await error_element.get_attribute("style")
    if style_attr and "display: list-item;" in style_attr:
        logger.warning("Error message appeared: %s", await error_element.text_content())
    else:
        logger.info("No error message appeared")


async def affirmative_opt_in(page: Page, data: dict[str, str]) -> None:
    """Select appropriate option when presented with affirmative opt-in choice."""
    if not await page.locator("li[class*='affirmative_optin_d_sharing']").count():
        logger.info("Action does not require affirmative opt-in")
        return
    logger.info("Action requires affirmative opt-in")
    if "opt_in" in data and data["opt_in"].lower() not in ["", "no"]:
        await page.locator("input[class*='affirmative_optin_radio']").first.check()
        logger.info("Submitting with subscription")
    else:
        await page.locator("input[class*='affirmative_optin_radio_no']").first.check()
        logger.info("Submitting without subscription")


async def fill_field(page: Page, field_name: str, field_value: str) -> None:
    """Fill in data in form field."""
    # Don't treat opt_in data as fillable form field
    if field_name == "opt_in":
        return
    form_field = page.locator(f"#form-{field_name}")
    if not form_field:
        logger.warning("Action does not contain %s field", field_name)
        return
    logger.info("Filling %s field", field_name)
    await form_field.fill(field_value)


async def fill_form(page: Page, signer_data: dict[str, str]) -> None:
    """Fill form fields at provided action network page with provided data."""
    for field_name, field_value in signer_data.items():
        await fill_field(page, field_name, field_value)

    wait_time = cryptogen.randint(500, 3000)
    await page.wait_for_timeout(wait_time)
    await affirmative_opt_in(page, signer_data)
    await submit_form(page)


@asynccontextmanager
async def create_browser_context(*, headless: bool = False) -> AsyncGenerator[BrowserContext, Any]:
    """Create and configure browser with Patchright's stealth mode."""
    with tempfile.TemporaryDirectory(prefix="patchright_") as temp_dir:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=temp_dir,
                channel="chrome",
                headless=headless,
                no_viewport=True,
            )

            try:
                yield context
            finally:
                await context.close()


@asynccontextmanager
async def get_browser_page(context: BrowserContext, *, require_new_page: bool = False) -> AsyncGenerator[Page, Any]:
    """Create a browser page ready to use."""
    # Reuse existing page if available, otherwise create new one
    pages = context.pages
    if pages and not require_new_page:
        page = pages[0]
    else:
        page = await context.new_page()

    try:
        yield page
    finally:
        await context.new_page()
        await page.close()


async def get_signers_from_csv(csv_path: Path) -> list[dict[str, str]]:
    """Load signer data from CSV and return it as a list of dicts."""
    with csv_path.open() as file:
        return list(DictReader(file))


async def get_inputs() -> tuple[Path, str, str | None]:
    """Collect path, action name, and source tag via user input."""
    csv_path = input("What's the path to the CSV file? ")
    action_name = input("What's the name of the action? (The part after 'actionnetwork.org/petitions/') ")
    source_tag = input("What source tag should be used? (Such as 'paper'; leave blank for no source tag) ")
    return Path(csv_path), action_name, source_tag


async def main() -> None:
    csv_path, action_name, source_tag = await get_inputs()
    action_url = f"https://actionnetwork.org/{ActionType.PETITION.value}s/{action_name}?kiosk=true"
    if source_tag:
        action_url = f"{action_url}&source={source_tag}"

    signers = await get_signers_from_csv(csv_path)
    async with create_browser_context() as context, get_browser_page(context) as page:
        for signer in tqdm(signers, unit="signer"):
            await page.goto(action_url)
            await fill_form(page, signer)


if __name__ == "__main__":
    asyncio.run(main())

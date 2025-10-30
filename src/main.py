"""Add signers from a CSV to an Action Network action via browser automation and kiosk mode."""

import asyncio
import logging
from contextlib import asynccontextmanager
from csv import DictReader
from enum import Enum
from pathlib import Path
from random import SystemRandom

from patchright.async_api import Page, async_playwright
from tqdm import tqdm
from typing_extensions import AsyncGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cryptogen = SystemRandom()


class ActionType(Enum):
    """Supported Action Network Action Types."""

    PETITION = "petition"
    FORM = "form"


async def fill_form(page: Page, data: dict[str, str]) -> None:
    """Fill form fields at provided action network page with provided data."""
    # Fill in the form fields
    for key, value in data.items():
        await page.locator(f"#form-{key}").fill(value)

    wait_time = cryptogen.randint(500, 3000)
    await page.wait_for_timeout(wait_time)

    await page.locator("[type=submit]").click()

    error_element = page.locator("#error_message")
    style_attr = await error_element.get_attribute("style")
    if style_attr and "display: list-item;" in style_attr:
        logger.warning("Error message appeared: %s", await error_element.text_content())
    else:
        logger.debug("No error message appeared")


async def get_inputs() -> tuple[Path, str, str | None]:
    """Collect path, action name, and source tag via user input."""
    csv_path = input("What's the path to the CSV file? ")
    action_name = input("What's the name of the action? (The part after 'actionnetwork.org/petitions/') ")
    source_tag = input("What source tag should be used? (Such as 'paper'; leave blank for no source tag) ")
    return Path(csv_path), action_name, source_tag


async def get_signers_from_csv(csv_path: Path) -> list[dict[str, str]]:
    """Load signer data from CSV and return it as a list of dicts."""
    with csv_path.open() as file:
        return list(DictReader(file))


@asynccontextmanager
async def browser_context() -> AsyncGenerator[Page]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            yield page
        finally:
            await browser.close()


async def main() -> None:
    csv_path, action_name, source_tag = await get_inputs()
    action_url = f"https://actionnetwork.org/{ActionType.PETITION}s/{action_name}?kiosk=true"
    if source_tag:
        action_url = f"{action_url}&source={source_tag}"

    async with browser_context() as page:
        signers = await get_signers_from_csv(csv_path)
        for signer in tqdm(signers, unit="signer"):
            await page.goto(action_url)
            await fill_form(page, signer)


if __name__ == "__main__":
    asyncio.run(main())

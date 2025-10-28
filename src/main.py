import asyncio
import logging
from csv import DictReader
from enum import Enum
from pathlib import Path
from random import SystemRandom

from patchright.async_api import async_playwright
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cryptogen = SystemRandom()


class ActionType(Enum):
    PETITION = "petition"
    FORM = "form"


async def fill_form(page, data: dict[str, str]):
    """
    Fill form fields at provided action network page with provided data.
    """

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


async def get_inputs() -> tuple[Path, str, str]:
    csv_path = input("What's the path to the CSV file? ")
    action_name = input("What's the name of the petition? (The part after 'actionnetwork.org/petitions/') ")
    source_tag = input("What source tag should be used? (Such as 'paper') ")
    return Path(csv_path), action_name, source_tag


async def get_signers_from_csv(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open() as file:
        signers = list(DictReader(file))
    return signers


async def main():
    csv_path, action_name, source_tag = get_inputs()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        signers = get_signers_from_csv(csv_path)
        for signer in tqdm(signers):
            action_url = f"https://actionnetwork.org/{ActionType.PETITION}s/{action_name}?kiosk=true"
            if source_tag:
                action_url = f"{action_url}&source={source_tag}"
            await page.goto(action_url)
            await fill_form(page, signer)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

import csv
import logging
from pathlib import Path
from random import SystemRandom

from patchright.sync_api import sync_playwright
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cryptogen = SystemRandom()


async def fill_form(page, data: dict[str, str]):
    """
    Fill form fields at provided action network url with provided data.

    Args:
    data (dict): Dictionary containing form data based on field ids:
    """

    # Fill in the form fields
    for key, value in data.items():
        page.fill(f"#form-{key}", value)

    wait_time = cryptogen.randint(500, 3000)
    await page.wait_for_timeout(wait_time)

    # Submit the form
    page.click("[type=submit]")

    error_element = page.locator("#error_message")
    style_attr = error_element.get_attribute("style")
    if style_attr and "display: list-item;" in style_attr:
        logger.warning(f"Error message appeared: {error_element.text_content()}")
    else:
        logger.debug("No error message appeared")


async def main():
    csv_path = input("What's the path to the CSV file?")
    action_type = "petition"
    action_name = input("What's the name of the petition? (The part after 'actionnetwork.org/petitions/')")
    source_tag = input("What source tag should be used? (Such as 'paper')")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        with Path(csv_path).open() as file:
            csv_reader = csv.DictReader(file)
            for signer in tqdm(csv_reader):
                page.goto(f"https://actionnetwork.org/{action_type}s/{action_name}?kiosk=true&source={source_tag}")
                await fill_form(page, signer)

        browser.close()


if __name__ == "__main__":
    main()

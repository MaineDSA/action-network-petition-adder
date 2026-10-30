import pytest

from src.main import ActionType, get_action_url


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("source_tag", "assembled_url"),
    [
        ("paper", "https://actionnetwork.org/petitions?/do_better#kiosk=true&source=paper"),
        ("", "https://actionnetwork.org/petitions?/do_better#kiosk=true"),
    ],
)
async def test_url_assembly(source_tag: str, assembled_url: str) -> None:
    action_type = ActionType.PETITION
    action_name = "do_better"

    action_url = await get_action_url(action_type, action_name, source_tag)

    assert action_url == assembled_url

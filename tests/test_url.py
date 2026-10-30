import pytest

from src.main import ActionType, get_action_url


@pytest.mark.asyncio
async def test_url_assembly() -> None:
    action_type = ActionType.PETITION
    action_name = "do_better"
    source_tag = "paper"

    action_url = await get_action_url(action_type, action_name, source_tag)

    assert action_url == "https://actionnetwork.org/petitions?/do_better#kiosk=true&source=paper"

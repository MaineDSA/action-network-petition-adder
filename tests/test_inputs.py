from pathlib import Path
from unittest.mock import patch

import pytest

from src.main import get_inputs


@pytest.mark.asyncio
async def test_get_inputs():
    known_csv_path = Path(__file__).parent / "test_resources/example.csv"
    known_action_name = "my-petition"
    known_source_tag = "paper"

    # Mock the input() calls with predetermined values
    with patch("builtins.input", side_effect=[known_csv_path, known_action_name, known_source_tag]):
        csv_path, action_name, source_tag = await get_inputs()

        assert csv_path == csv_path
        assert action_name == known_action_name
        assert source_tag == known_source_tag

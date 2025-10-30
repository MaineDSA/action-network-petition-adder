from pathlib import Path
from unittest.mock import patch

import pytest

from src.main import get_inputs


@pytest.mark.asyncio
async def test_get_inputs() -> None:
    known_csv_path = Path(__file__).parent / "test_resources/example.csv"
    known_action_name = "my-petition"
    known_source_tag = "paper"

    def mock_input(prompt: str) -> str:
        if "path to the CSV file" in prompt:
            return str(known_csv_path)
        if "name of the action" in prompt:
            return known_action_name
        if "source tag" in prompt:
            return known_source_tag
        msg = f"Unexpected prompt: {prompt}"
        raise ValueError(msg)

    with patch("builtins.input", side_effect=mock_input):
        csv_path, action_name, source_tag = await get_inputs()

        assert csv_path == known_csv_path
        assert action_name == known_action_name
        assert source_tag == known_source_tag


@pytest.mark.asyncio
async def test_get_inputs_no_source() -> None:
    known_csv_path = Path(__file__).parent / "test_resources/example.csv"
    known_action_name = "my-petition"
    known_source_tag = "paper"  # noqa F841

    def mock_input(prompt: str) -> str:
        if "path to the CSV file" in prompt:
            return str(known_csv_path)
        if "name of the action" in prompt:
            return known_action_name
        if "source tag" in prompt:
            return ""
        msg = f"Unexpected prompt: {prompt}"
        raise ValueError(msg)

    with patch("builtins.input", side_effect=mock_input):
        csv_path, action_name, source_tag = await get_inputs()

        assert csv_path == known_csv_path
        assert action_name == known_action_name
        assert not source_tag

from pathlib import Path

from src.main import get_signers_from_csv


async def test_load_signers() -> None:
    signers = await get_signers_from_csv(Path(__file__).parent / "test_resources/example.csv")

    assert signers[0]["first_name"] == "Eugene"
    assert signers[0]["last_name"] == "Debs"
    assert signers[0]["email"] == "edebs@iww.org"
    assert signers[0]["zip"] == "47801"

    assert signers[1]["first_name"] == "Gurley"
    assert signers[1]["last_name"] == "Flynn"
    assert signers[1]["email"] == "egurley@cpusa.org"
    assert signers[1]["zip"] == "01840"

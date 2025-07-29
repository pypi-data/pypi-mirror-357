import pytest

from yandex_summary import YandexSummaryAPI


@pytest.mark.asyncio
async def test_invalid_api_key():
    api = YandexSummaryAPI(api_key="")
    with pytest.raises(ValueError, match="API key cannot be empty"):
        await api.get_summary("https://example.com", summary_type="detailed")


@pytest.mark.asyncio
async def test_invalid_summary_type():
    api = YandexSummaryAPI(api_key="dummy-key")
    result = await api.get_summary(
        "https://example.com", summary_type="invalid"
    )
    assert (
        result.error
        == "Invalid summary_type: invalid. Use 'short' or 'detailed'."
    )

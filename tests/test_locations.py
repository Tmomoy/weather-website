import pytest

from app.domain.locations import InvalidLocation, normalize_location


@pytest.mark.parametrize(("raw", "expected"), [
    ("台北", "臺北市"),
    (" 臺中市 ", "臺中市"),
    ("板橋區", "新北市"),
    ("花蓮", "花蓮縣"),
])
def test_normalize_location(raw, expected):
    assert normalize_location(raw) == expected


@pytest.mark.parametrize("raw", ["", "火星市", "未知地區"])
def test_invalid_location(raw):
    with pytest.raises(InvalidLocation):
        normalize_location(raw)

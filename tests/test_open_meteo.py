from datetime import datetime, timedelta

from app.services.open_meteo_client import parse_open_meteo


def test_parse_open_meteo_forecast():
    start = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    hourly_times = [(start + timedelta(hours=index)).isoformat(timespec="minutes") for index in range(37)]
    today = start.date()
    payload = {
        "hourly": {
            "time": hourly_times,
            "temperature_2m": [28 + index / 10 for index in range(37)],
            "precipitation_probability": [20] * 37,
            "weather_code": [2] * 37,
        },
        "daily": {
            "time": [(today + timedelta(days=index)).isoformat() for index in range(7)],
            "temperature_2m_min": [25] * 7,
            "temperature_2m_max": [33] * 7,
            "precipitation_probability_max": [40] * 7,
            "weather_code": [61] * 7,
        },
    }
    hourly, daily = parse_open_meteo(payload)
    assert len(hourly) == 3
    assert len(daily) == 7
    assert hourly[0].summary == "局部多雲"
    assert daily[0].summary == "小雨"

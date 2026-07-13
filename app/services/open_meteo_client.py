from datetime import datetime
from typing import Any

import requests

from app.domain.locations import CITY_COORDINATES
from app.domain.models import ForecastPeriod
from app.services.cwa_client import WeatherApiError, WeatherDataError, _to_int


WEATHER_CODES = {
    0: "晴朗", 1: "大致晴朗", 2: "局部多雲", 3: "陰天",
    45: "有霧", 48: "霧淞", 51: "毛毛雨", 53: "毛毛雨",
    55: "較強毛毛雨", 56: "凍毛毛雨", 57: "強凍毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨", 66: "凍雨", 67: "強凍雨",
    71: "小雪", 73: "中雪", 75: "大雪", 77: "霰",
    80: "局部陣雨", 81: "陣雨", 82: "強陣雨",
    85: "陣雪", 86: "強陣雪", 95: "雷雨", 96: "雷雨伴冰雹", 99: "強雷雨伴冰雹",
}


def _value(values: list[Any], index: int) -> Any:
    return values[index] if index < len(values) else None


def _summary(code: Any) -> str:
    return WEATHER_CODES.get(_to_int(code), "天氣狀況未明")


def parse_open_meteo(payload: dict[str, Any]) -> tuple[list[ForecastPeriod], list[ForecastPeriod]]:
    hourly_data = payload.get("hourly", {})
    daily_data = payload.get("daily", {})
    now = datetime.now()
    all_hourly: list[ForecastPeriod] = []

    for index, value in enumerate(hourly_data.get("time", [])):
        try:
            start = datetime.fromisoformat(value)
        except (TypeError, ValueError):
            continue
        if start < now.replace(minute=0, second=0, microsecond=0):
            continue
        temperature = _to_int(_value(hourly_data.get("temperature_2m", []), index))
        all_hourly.append(ForecastPeriod(
            start_time=start,
            summary=_summary(_value(hourly_data.get("weather_code", []), index)),
            min_temp_c=temperature,
            max_temp_c=temperature,
            rain_probability=_to_int(_value(hourly_data.get("precipitation_probability", []), index)),
        ))

    hourly = all_hourly[::12][:3]
    daily: list[ForecastPeriod] = []
    for index, value in enumerate(daily_data.get("time", [])):
        try:
            start = datetime.fromisoformat(value)
        except (TypeError, ValueError):
            continue
        daily.append(ForecastPeriod(
            start_time=start,
            summary=_summary(_value(daily_data.get("weather_code", []), index)),
            min_temp_c=_to_int(_value(daily_data.get("temperature_2m_min", []), index)),
            max_temp_c=_to_int(_value(daily_data.get("temperature_2m_max", []), index)),
            rain_probability=_to_int(_value(daily_data.get("precipitation_probability_max", []), index)),
        ))

    if not hourly and not daily:
        raise WeatherDataError("備援天氣服務目前沒有可用資料。")
    return hourly, daily


class OpenMeteoClient:
    URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout: tuple[float, float] = (3.05, 10)) -> None:
        self.timeout = timeout

    def get_forecast(self, city: str) -> tuple[list[ForecastPeriod], list[ForecastPeriod]]:
        latitude, longitude = CITY_COORDINATES[city]
        try:
            response = requests.get(self.URL, params={
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "temperature_2m,precipitation_probability,weather_code",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "Asia/Taipei",
                "forecast_days": 7,
            }, timeout=self.timeout)
            response.raise_for_status()
            return parse_open_meteo(response.json())
        except requests.Timeout as exc:
            raise WeatherApiError("備援天氣服務回應逾時。") from exc
        except (requests.RequestException, ValueError) as exc:
            raise WeatherApiError("備援天氣服務暫時無法使用。") from exc

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.domain.models import ForecastPeriod


class WeatherApiError(RuntimeError):
    pass


class WeatherApiConfigurationError(WeatherApiError):
    pass


class WeatherDataError(WeatherApiError):
    pass


def _first(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _parse_time(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> Optional[int]:
    if value in (None, "", "-"):
        return None
    try:
        return round(float(value))
    except (TypeError, ValueError):
        return None


def _time_value(item: dict[str, Any]) -> Any:
    parameter = _first(item, "parameter", "Parameter", default={}) or {}
    parameter_value = _first(parameter, "parameterName", "ParameterName")
    if parameter_value is not None:
        return parameter_value

    values = _first(item, "elementValue", "ElementValue", default=[]) or []
    if not values:
        return None
    value = values[0]
    if not isinstance(value, dict):
        return value
    return _first(
        value, "value", "Value", "Weather", "Temperature", "MaxTemperature",
        "MinTemperature", "ProbabilityOfPrecipitation",
    )


def _locations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = _first(payload, "records", "Records", default={}) or {}
    direct = _first(records, "location", "Location")
    if isinstance(direct, list):
        return direct
    groups = _first(records, "locations", "Locations", default=[]) or []
    result: list[dict[str, Any]] = []
    for group in groups:
        result.extend(_first(group, "location", "Location", default=[]) or [])
    return result


def _element_map(location: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    elements = _first(location, "weatherElement", "WeatherElement", default=[]) or []
    return {
        str(_first(element, "elementName", "ElementName", default="")): (
            _first(element, "time", "Time", default=[]) or []
        )
        for element in elements
    }


def _pick_element(
    elements: dict[str, list[dict[str, Any]]], names: Iterable[str]
) -> list[dict[str, Any]]:
    for name in names:
        if name in elements:
            return elements[name]
    return []


def _at(items: list[dict[str, Any]], index: int) -> dict[str, Any]:
    return items[index] if index < len(items) else {}


def parse_forecast(payload: dict[str, Any], city: str) -> list[ForecastPeriod]:
    matching = next(
        (item for item in _locations(payload)
         if _first(item, "locationName", "LocationName") == city),
        None,
    )
    if not matching:
        raise WeatherDataError("中央氣象署回應中沒有指定地區的資料。")

    elements = _element_map(matching)
    weather = _pick_element(elements, ("Wx", "天氣現象"))
    minimum = _pick_element(elements, ("MinT", "最低溫度"))
    maximum = _pick_element(elements, ("MaxT", "最高溫度", "平均溫度", "T"))
    rain = _pick_element(elements, ("PoP", "PoP12h", "12小時降雨機率"))
    count = max(map(len, (weather, minimum, maximum, rain)), default=0)
    periods: list[ForecastPeriod] = []

    for index in range(count):
        reference = _at(weather, index) or _at(maximum, index) or _at(minimum, index)
        start = _parse_time(_first(reference, "startTime", "StartTime", "dataTime", "DataTime"))
        if not start:
            continue
        periods.append(ForecastPeriod(
            start_time=start,
            end_time=_parse_time(_first(reference, "endTime", "EndTime")),
            summary=str(_time_value(_at(weather, index)) or "--"),
            min_temp_c=_to_int(_time_value(_at(minimum, index))),
            max_temp_c=_to_int(_time_value(_at(maximum, index))),
            rain_probability=_to_int(_time_value(_at(rain, index))),
        ))

    if not periods:
        raise WeatherDataError("預報資料目前為空。")
    return periods


class CwaClient:
    THIRTY_SIX_HOUR_DATASET = "F-C0032-001"
    WEEKLY_CITY_DATASET = "F-C0032-005"

    def __init__(self, api_key: str, base_url: str,
                 timeout: tuple[float, float] = (3.05, 10),
                 session: Optional[requests.Session] = None) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or self._build_session()

    @staticmethod
    def _build_session() -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=2, connect=2, read=1, status=2, backoff_factor=0.3,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
        )
        session.mount("https://", HTTPAdapter(max_retries=retry))
        return session

    def _get(self, dataset: str, city: str) -> dict[str, Any]:
        if not self.api_key:
            raise WeatherApiConfigurationError("尚未設定 CWA_API_KEY。")
        try:
            response = self.session.get(
                f"{self.base_url}/{dataset}",
                params={"Authorization": self.api_key, "locationName": city},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.Timeout as exc:
            raise WeatherApiError("中央氣象署服務回應逾時，請稍後再試。") from exc
        except requests.RequestException as exc:
            raise WeatherApiError("暫時無法連線中央氣象署服務。") from exc
        except ValueError as exc:
            raise WeatherDataError("中央氣象署回傳了無法解析的資料。") from exc
        if payload.get("success") in ("false", False):
            raise WeatherApiError("中央氣象署未接受這次查詢。")
        return payload

    def get_36_hour_forecast(self, city: str) -> list[ForecastPeriod]:
        return parse_forecast(self._get(self.THIRTY_SIX_HOUR_DATASET, city), city)

    def get_weekly_forecast(self, city: str) -> list[ForecastPeriod]:
        return parse_forecast(self._get(self.WEEKLY_CITY_DATASET, city), city)

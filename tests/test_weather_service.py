from datetime import datetime

from app.domain.models import ForecastPeriod
from app.services.cwa_client import WeatherApiError
from app.services.weather_service import WeatherService


def period(day=13):
    return ForecastPeriod(
        start_time=datetime.fromisoformat(f"2026-07-{day:02d}T06:00:00+08:00"),
        summary="晴",
        min_temp_c=25,
        max_temp_c=33,
    )


class CountingClient:
    def __init__(self):
        self.calls = 0

    def get_36_hour_forecast(self, city):
        self.calls += 1
        return [period()]

    def get_weekly_forecast(self, city):
        self.calls += 1
        return [period(), period(), period(14)]


def test_service_caches_and_deduplicates_days():
    client = CountingClient()
    service = WeatherService(client, cache_ttl=60)
    first = service.get_weather("台北")
    second = service.get_weather("臺北市")
    assert first is second
    assert len(first.daily) == 2
    assert client.calls == 2


class PartialClient:
    def get_36_hour_forecast(self, city):
        raise WeatherApiError("36 小時資料失敗")

    def get_weekly_forecast(self, city):
        return [period()]


def test_service_returns_partial_result_with_warning():
    report = WeatherService(PartialClient(), cache_ttl=0).get_weather("臺北市")
    assert report.daily
    assert report.warnings == ["36 小時資料失敗"]

from datetime import datetime

import pytest

from app import create_app
from app.config import TestingConfig
from app.domain.models import ForecastPeriod, WeatherReport


class FakeWeatherService:
    def get_weather(self, location):
        if location == "服務失敗":
            from app.services.cwa_client import WeatherApiError
            raise WeatherApiError("測試服務失敗")
        period = ForecastPeriod(
            start_time=datetime.fromisoformat("2026-07-13T06:00:00+08:00"),
            end_time=datetime.fromisoformat("2026-07-13T18:00:00+08:00"),
            summary="晴時多雲",
            min_temp_c=27,
            max_temp_c=34,
            rain_probability=20,
        )
        return WeatherReport(
            location="臺北市",
            updated_at=datetime.fromisoformat("2026-07-13T08:00:00+08:00"),
            current=period,
            hourly=[period],
            daily=[period],
        )


@pytest.fixture()
def app():
    return create_app(TestingConfig, weather_service=FakeWeatherService())


@pytest.fixture()
def client(app):
    return app.test_client()

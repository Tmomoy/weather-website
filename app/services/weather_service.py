from datetime import datetime
from threading import Lock
from time import monotonic

from app.domain.locations import normalize_location
from app.domain.models import ForecastPeriod, WeatherReport
from app.services.cwa_client import CwaClient, WeatherApiError


class WeatherService:
    def __init__(self, client: CwaClient, cache_ttl: int = 600, fallback_client=None) -> None:
        self.client = client
        self.fallback_client = fallback_client
        self.cache_ttl = cache_ttl
        self._cache: dict[str, tuple[float, WeatherReport]] = {}
        self._lock = Lock()

    def get_weather(self, location: str) -> WeatherReport:
        city = normalize_location(location)
        cached = self._get_cached(city)
        if cached:
            return cached

        warnings: list[str] = []
        hourly: list[ForecastPeriod] = []
        daily: list[ForecastPeriod] = []
        try:
            hourly = self.client.get_36_hour_forecast(city)
        except WeatherApiError as exc:
            warnings.append(str(exc))
        try:
            daily = self._one_period_per_day(self.client.get_weekly_forecast(city))
        except WeatherApiError as exc:
            warnings.append(str(exc))

        if not hourly and not daily and self.fallback_client:
            try:
                hourly, daily = self.fallback_client.get_forecast(city)
                warnings = ["目前顯示備援預報資料。"]
            except WeatherApiError as exc:
                warnings.append(str(exc))

        if not hourly and not daily:
            raise WeatherApiError(warnings[-1] if warnings else "目前沒有可用的天氣資料。")

        report = WeatherReport(
            location=city,
            updated_at=datetime.now().astimezone(),
            current=hourly[0] if hourly else daily[0],
            hourly=hourly,
            daily=daily[:7],
            warnings=list(dict.fromkeys(warnings)),
        )
        self._store(city, report)
        return report

    @staticmethod
    def _one_period_per_day(periods: list[ForecastPeriod]) -> list[ForecastPeriod]:
        result: list[ForecastPeriod] = []
        seen = set()
        for period in periods:
            day = period.start_time.date()
            if day not in seen:
                result.append(period)
                seen.add(day)
        return result

    def _get_cached(self, city: str) -> WeatherReport | None:
        if self.cache_ttl <= 0:
            return None
        with self._lock:
            cached = self._cache.get(city)
            if cached and cached[0] > monotonic():
                return cached[1]
            self._cache.pop(city, None)
        return None

    def _store(self, city: str, report: WeatherReport) -> None:
        if self.cache_ttl > 0:
            with self._lock:
                self._cache[city] = (monotonic() + self.cache_ttl, report)

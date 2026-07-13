from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ForecastPeriod:
    start_time: datetime
    end_time: Optional[datetime] = None
    summary: str = "--"
    min_temp_c: Optional[int] = None
    max_temp_c: Optional[int] = None
    rain_probability: Optional[int] = None


@dataclass(frozen=True)
class WeatherReport:
    location: str
    updated_at: datetime
    current: ForecastPeriod
    hourly: list[ForecastPeriod] = field(default_factory=list)
    daily: list[ForecastPeriod] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

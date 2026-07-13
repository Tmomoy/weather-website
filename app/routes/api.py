from flask import Blueprint, current_app, jsonify, request

from app.domain.locations import InvalidLocation, SEARCHABLE_LOCATIONS
from app.domain.models import ForecastPeriod, WeatherReport
from app.services.cwa_client import WeatherApiError

api = Blueprint("api", __name__, url_prefix="/api/v1")


def _period_json(period: ForecastPeriod) -> dict:
    return {
        "start_time": period.start_time.isoformat(),
        "end_time": period.end_time.isoformat() if period.end_time else None,
        "summary": period.summary,
        "min_temp_c": period.min_temp_c,
        "max_temp_c": period.max_temp_c,
        "rain_probability": period.rain_probability,
    }


def _report_json(report: WeatherReport) -> dict:
    return {
        "location": report.location,
        "updated_at": report.updated_at.isoformat(),
        "current": _period_json(report.current),
        "hourly": [_period_json(item) for item in report.hourly],
        "daily": [_period_json(item) for item in report.daily],
        "warnings": report.warnings,
    }


@api.get("/locations")
def locations():
    return jsonify({"locations": SEARCHABLE_LOCATIONS})


@api.get("/weather")
def weather():
    try:
        report = current_app.extensions["weather_service"].get_weather(
            request.args.get("city", "")
        )
    except InvalidLocation as exc:
        return jsonify({"error": {"code": "invalid_location", "message": str(exc)}}), 400
    except WeatherApiError as exc:
        current_app.logger.warning("API weather lookup failed: %s", exc)
        return jsonify({"error": {"code": "weather_unavailable", "message": str(exc)}}), 503
    return jsonify({"data": _report_json(report)})

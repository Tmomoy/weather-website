from flask import Blueprint, current_app, jsonify, render_template, request

from app.domain.locations import InvalidLocation, SEARCHABLE_LOCATIONS
from app.services.cwa_client import WeatherApiError

bp = Blueprint("weather", __name__)


@bp.get("/")
def home():
    return render_template("index.html", locations=SEARCHABLE_LOCATIONS)


@bp.route("/weather", methods=["GET", "POST"])
def weather():
    location = request.values.get("city", "")
    try:
        report = current_app.extensions["weather_service"].get_weather(location)
    except InvalidLocation as exc:
        return render_template(
            "index.html", locations=SEARCHABLE_LOCATIONS,
            error=str(exc), query=location,
        ), 400
    except WeatherApiError as exc:
        current_app.logger.warning("Weather lookup failed: %s", exc)
        return render_template("error.html", message=str(exc), query=location), 503
    return render_template("result.html", report=report)


@bp.get("/health")
def health():
    return jsonify(status="ok")

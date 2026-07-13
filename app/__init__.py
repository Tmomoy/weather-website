from flask import Flask

from app.config import Config
from app.routes.weather import bp
from app.routes.api import api
from app.services.cwa_client import CwaClient
from app.services.open_meteo_client import OpenMeteoClient
from app.services.weather_service import WeatherService


def create_app(config_object=Config, weather_service=None) -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config_object)
    app.json.ensure_ascii = False

    if weather_service is None:
        client = CwaClient(
            api_key=app.config["CWA_API_KEY"],
            base_url=app.config["CWA_API_BASE_URL"],
            timeout=(app.config["CWA_CONNECT_TIMEOUT"], app.config["CWA_READ_TIMEOUT"]),
        )
        fallback_client = OpenMeteoClient(timeout=(
            app.config["CWA_CONNECT_TIMEOUT"], app.config["CWA_READ_TIMEOUT"]
        ))
        weather_service = WeatherService(
            client, app.config["WEATHER_CACHE_TTL"], fallback_client=fallback_client
        )

    app.extensions["weather_service"] = weather_service
    app.register_blueprint(bp)
    app.register_blueprint(api)
    return app

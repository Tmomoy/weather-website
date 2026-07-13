import os


class Config:
    CWA_API_KEY = os.getenv("CWA_API_KEY", "")
    CWA_API_BASE_URL = os.getenv(
        "CWA_API_BASE_URL", "https://opendata.cwa.gov.tw/api/v1/rest/datastore"
    )
    CWA_CONNECT_TIMEOUT = float(os.getenv("CWA_CONNECT_TIMEOUT", "3.05"))
    CWA_READ_TIMEOUT = float(os.getenv("CWA_READ_TIMEOUT", "10"))
    WEATHER_CACHE_TTL = int(os.getenv("WEATHER_CACHE_TTL", "600"))
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    JSON_AS_ASCII = False


class TestingConfig(Config):
    TESTING = True
    CWA_API_KEY = "test-key"
    WEATHER_CACHE_TTL = 0

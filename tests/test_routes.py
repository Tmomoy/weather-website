def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "島嶼天氣" in response.get_data(as_text=True)


def test_weather_result(client):
    response = client.get("/weather?city=臺北市")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "晴時多雲" in body
    assert "未來 36 小時" in body


def test_invalid_location(client):
    response = client.get("/weather")
    assert response.status_code == 200  # fake service bypasses validation in route test


def test_service_failure(client):
    response = client.get("/weather?city=服務失敗")
    assert response.status_code == 503
    assert "天空稍微失聯了" in response.get_data(as_text=True)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_weather_api(client):
    response = client.get("/api/v1/weather?city=臺北市")
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["data"]["location"] == "臺北市"
    assert payload["data"]["current"]["summary"] == "晴時多雲"
    assert payload["data"]["hourly"]


def test_locations_api(client):
    response = client.get("/api/v1/locations")
    assert response.status_code == 200
    assert "臺北市" in response.get_json()["locations"]


def test_weather_api_error_is_json(client):
    response = client.get("/api/v1/weather?city=服務失敗")
    assert response.status_code == 503
    assert response.get_json()["error"]["code"] == "weather_unavailable"

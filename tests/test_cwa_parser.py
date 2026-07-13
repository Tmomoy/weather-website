from app.services.cwa_client import WeatherDataError, parse_forecast


def test_parse_forecast_by_element_name_not_array_order():
    payload = {
        "success": "true",
        "records": {
            "location": [{
                "locationName": "臺北市",
                "weatherElement": [
                    {"elementName": "PoP", "time": [{
                        "startTime": "2026-07-13T06:00:00+08:00",
                        "endTime": "2026-07-13T18:00:00+08:00",
                        "parameter": {"parameterName": "30"},
                    }]},
                    {"elementName": "MaxT", "time": [{
                        "startTime": "2026-07-13T06:00:00+08:00",
                        "parameter": {"parameterName": "35"},
                    }]},
                    {"elementName": "Wx", "time": [{
                        "startTime": "2026-07-13T06:00:00+08:00",
                        "parameter": {"parameterName": "晴時多雲"},
                    }]},
                    {"elementName": "MinT", "time": [{
                        "startTime": "2026-07-13T06:00:00+08:00",
                        "parameter": {"parameterName": "27"},
                    }]},
                ],
            }],
        },
    }

    result = parse_forecast(payload, "臺北市")

    assert len(result) == 1
    assert result[0].summary == "晴時多雲"
    assert result[0].min_temp_c == 27
    assert result[0].max_temp_c == 35
    assert result[0].rain_probability == 30


def test_parse_new_title_case_fields():
    payload = {
        "Records": {"Locations": [{"Location": [{
            "LocationName": "臺北市",
            "WeatherElement": [{
                "ElementName": "天氣現象",
                "Time": [{
                    "StartTime": "2026-07-14T06:00:00+08:00",
                    "ElementValue": [{"Weather": "多雲"}],
                }],
            }],
        }]}]},
    }
    assert parse_forecast(payload, "臺北市")[0].summary == "多雲"


def test_missing_location_is_explicit_error():
    try:
        parse_forecast({"records": {"location": []}}, "臺北市")
    except WeatherDataError as error:
        assert "沒有指定地區" in str(error)
    else:
        raise AssertionError("WeatherDataError was not raised")

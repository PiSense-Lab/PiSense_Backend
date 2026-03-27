# import pytest
import pytest
from datetime import date, time
from pisense.backend.models.weather_models import (
    HourlyRecord,
    DailyRecord,
    WeatherResponse
)

from fastapi.testclient import TestClient
from pisense.api.main import app
from unittest.mock import patch


def test_root():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_hourly_record_valid():
    record = HourlyRecord(
        date=date(2026, 3, 27),
        time=time(12, 0),
        temperature_2m=50.0
    )

    assert record.temperature_2m == 50.0
    assert record.date.year == 2026


def test_hourly_record_optional_fields():
    record = HourlyRecord(
        date=date(2026, 3, 27),
        time=time(12, 0)
    )

    assert record.temperature_2m is None
    assert record.precipitation is None


def test_daily_record_valid():
    record = DailyRecord(
        date=date(2026, 3, 27),
        time=time(0, 0),
        temperature_2m_max=60.0
    )

    assert record.temperature_2m_max == 60.0


def test_weather_response_hourly_only():
    response = WeatherResponse(
        hourly=[HourlyRecord(date=date(2026, 3, 27), time=time(0, 0))]
    )

    assert response.hourly is not None
    assert response.daily is None


def test_weather_response_daily_only():
    response = WeatherResponse(
        daily=[DailyRecord(date=date(2026, 3, 27), time=time(0, 0))]
    )

    assert response.daily is not None
    assert response.hourly is None


def test_invalid_hourly_record():
    with pytest.raises(Exception):
        HourlyRecord(
            date="not-a-date",
            time="not-a-time"
        )

def mock_hourly_response():
    return {
        "hourly": [
            {
                "date": "2026-03-27",
                "time": "00:00:00",
                "temperature_2m": 50.0
            }
        ]
    }


def mock_daily_response():
    return {
        "daily": [
            {
                "date": "2026-03-27",
                "time": "00:00:00",
                "temperature_2m_max": 60.0
            }
        ]
    }


def test_forecast_hourly_route(client):
    from unittest.mock import patch

    with patch("pisense.backend.routes.weather.get_forecast_weather_hourly") as mock_service:
        mock_service.return_value = mock_hourly_response()
        res = client.get("/weather/forecast-weather/hourly")

    assert res.status_code == 200
    data = res.json()
    assert "hourly" in data
    assert data["hourly"][0]["temperature_2m"] == 50.0

def test_forecast_daily_route(client):
    from unittest.mock import patch

    with patch("pisense.backend.routes.weather.get_forecast_weather_daily") as mock_service:
        mock_service.return_value = mock_daily_response()
        res = client.get("/weather/forecast-weather/daily")

    assert res.status_code == 200
    data = res.json()
    assert "daily" in data
    assert data["daily"][0]["temperature_2m_max"] == 60.0


@patch("pisense.backend.services.weather_service.get_historical_weather_hourly")
def test_historical_hourly_route(mock_service, client):
    mock_service.return_value = mock_hourly_response()

    res = client.get("/weather/historical-weather/hourly")

    assert res.status_code == 200
    assert "hourly" in res.json()


@patch("pisense.backend.services.weather_service.get_historical_weather_daily")
def test_historical_daily_route(mock_service, client):
    mock_service.return_value = mock_daily_response()

    res = client.get("/weather/historical-weather/daily")

    assert res.status_code == 200
    assert "daily" in res.json()

@patch("pisense.backend.services.weather_service.get_forecast_weather_hourly")
def test_response_schema_shape(mock_service, client):
    mock_service.return_value = mock_hourly_response()

    res = client.get("/weather/forecast-weather/hourly")
    data = res.json()

    assert isinstance(data, dict)
    assert "hourly" in data or "daily" in data
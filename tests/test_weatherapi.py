# import pytest
from datetime import date, time

from fastapi.testclient import TestClient
from build.lib.pisense.backend.models.weather_models import HourlyRecord, DailyRecord
from pisense.api.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_get_historical_weather():
    response = client.get("/weather/historical-weather")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    # Validate each item using Pydantic
    validated = [HourlyRecord.model_validate(item) for item in data]

    assert len(validated) == len(data)

    # stronger checks
    for record in validated:
        assert isinstance(record.date, date)
        assert isinstance(record.time, time)
        assert isinstance(record.temperature_2m, float)

def test_get_daily_weather():
    response = client.get("/weather/daily-weather")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    # Validate each item using Pydantic
    validated = [DailyRecord.model_validate(item) for item in data]

    assert len(validated) == len(data)

    # stronger checks
    for record in validated:
        assert isinstance(record.date, date)
        assert isinstance(record.time, time)
        assert isinstance(record.temperature_2m_max, float)
        assert isinstance(record.temperature_2m_min, float)
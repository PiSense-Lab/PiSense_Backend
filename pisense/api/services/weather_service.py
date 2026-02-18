import pandas as pd
from datetime import datetime
from models.weather_models import HourlyRecord
from clients.openmeteo_client import openmeteo_client


def _build_hourly_records(hourly) -> list[HourlyRecord]:
    """
    Shared transformer for hourly weather blocks.
    """

    temps = hourly.Variables(0).ValuesAsNumpy()

    dates = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )

    df = pd.DataFrame({
        "date": dates,
        "temperature_2m": temps
    })

    return [
        HourlyRecord(
            date=row.date.to_pydatetime(),
            temperature_2m=float(row.temperature_2m)
        )
        for row in df.itertuples(index=False)
    ]


def get_forecast_weather():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": 46.73,
        "longitude": 94.69,
        "hourly": ["temperature_2m"],
    }

    responses = openmeteo_client.weather_api(
        url,
        params=params
    )

    response = responses[0]
    hourly = response.Hourly()

    return _build_hourly_records(hourly)


def get_historical_weather():
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

    params = {
        "latitude": 46.73,
        "longitude": 94.69,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "hourly": "temperature_2m",
        "temperature_unit": "fahrenheit",
    }

    responses = openmeteo_client.weather_api(
        url,
        params=params
    )

    response = responses[0]
    hourly = response.Hourly()

    return _build_hourly_records(hourly)
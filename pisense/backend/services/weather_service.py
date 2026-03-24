import pandas as pd
from pisense.backend.models.weather_models import HourlyRecord, DailyRecord
from pisense.backend.clients.openmeteo_client import openmeteo_client
from pisense.backend.utils.weather_utils import map_to_models, add_date_time_columns, build_dataframe


def _build_hourly_records(hourly) -> list[HourlyRecord]:
    df = build_dataframe(hourly, {
        "temperature_2m": 0
    })

    df = add_date_time_columns(df)

    return map_to_models(df, HourlyRecord, {
        "date": "date",
        "time": "time",
        "temperature_2m": "temperature_2m"
    })

def _build_daily_records(daily) -> list[DailyRecord]:
    """
    Shared transformer for daily weather blocks.
    """

    temp_max = daily.Variables(0).ValuesAsNumpy()
    temp_min = daily.Variables(1).ValuesAsNumpy()

    dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left"
    )

    df = pd.DataFrame({
        "datetime": dates,
        "temperature_2m_max": temp_max,
        "temperature_2m_min": temp_min
    })

    # split datetime
    df["date"] = df["datetime"].dt.date
    df["time"] = df["datetime"].dt.time

    return [
        DailyRecord(
            date=row.date,
            time=row.time,
            temperature_2m_max=float(row.temperature_2m_max),
            temperature_2m_min=float(row.temperature_2m_min)
        )
        for row in df.itertuples(index=False)
    ]


def get_forecast_weather(latitude: float, longitude: float, forecast_days: int):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m"],
        "temperature_unit": "fahrenheit",
        "forecast_days": forecast_days,
    }

    responses = openmeteo_client.weather_api(
        url,
        params=params
    )

    response = responses[0]
    hourly = response.Hourly()

    return _build_hourly_records(hourly)


def get_forecast_day_weather(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "temperature_unit": "fahrenheit",
    }

    responses = openmeteo_client.weather_api(
        url,
        params=params
    )

    response = responses[0]
    daily = response.Daily()

    return _build_daily_records(daily)


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

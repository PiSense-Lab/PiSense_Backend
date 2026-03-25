import pandas as pd
from pisense.backend.models.weather_models import HOURLY_VARIABLES, DAILY_VARIABLES, HourlyRecord, DailyRecord
from pisense.backend.clients.openmeteo_client import openmeteo_client
from pisense.backend.utils.weather_utils import map_to_models, add_date_time_columns, build_dataframe


def _build_hourly_records(hourly) -> list[HourlyRecord]:
    df = build_dataframe(hourly, HOURLY_VARIABLES)

    df = add_date_time_columns(df)

    field_map = {
        "date": "date",
        "time": "time",
        **{k: k for k in HOURLY_VARIABLES.keys()}
    }
    return map_to_models(
        df,
        HourlyRecord,
        field_map,
        float_fields=set(HOURLY_VARIABLES.keys())
    )

def _build_daily_records(daily) -> list[DailyRecord]:
    df = build_dataframe(daily, DAILY_VARIABLES)

    df = add_date_time_columns(df)

    field_map = {
        "date": "date",
        "time": "time",
        **{k: k for k in DAILY_VARIABLES.keys()}
    }
    return map_to_models(
        df,
        DailyRecord,
        field_map,
        float_fields=set(DAILY_VARIABLES.keys())
    )

def get_forecast_weather_hourly(latitude: float, longitude: float, forecast_days: int):
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


def get_forecast_weather_daily(latitude: float, longitude: float, forecast_days: int):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min"],
        "temperature_unit": "fahrenheit",
        "forecast_days": forecast_days,
    }

    responses = openmeteo_client.weather_api(
        url,
        params=params
    )

    response = responses[0]
    daily = response.Daily()

    return _build_daily_records(daily)

# get the historical weather but daily and hourly, with start_date and end_date params
def get_historical_weather(latitude: float, longitude: float, start_date: str, end_date: str):
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
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


# testing function to call both hourly and daily
# Daily - forcast days param
# hourly - forcast days param, start_date, end_date
def get_weather_forecast(latitude, longitude, hourly=False, daily=False, **kwargs):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_unit": "fahrenheit",
        **kwargs
    }

    if hourly:
        params["hourly"] = list(HOURLY_VARIABLES.keys())

    if daily:
        params["daily"] = list(DAILY_VARIABLES.keys())

    responses = openmeteo_client.weather_api(url, params=params)
    response = responses[0]

    result = {}

    if hourly:
        result["hourly"] = _build_hourly_records(response.Hourly())

    if daily:
        result["daily"] = _build_daily_records(response.Daily())

    return result
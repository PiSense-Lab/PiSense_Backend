import pandas as pd
from pisense.backend.models.weather_models import HOURLY_FIELDS, DAILY_FIELDS, HourlyRecord, DailyRecord
from pisense.backend.clients.openmeteo_client import openmeteo_client
from pisense.backend.utils.weather_utils import map_to_models, add_date_time_columns, build_dataframe

# helper functions to build hourly and daily records from the API response
def _build_hourly_records(hourly) -> list[HourlyRecord]:
    selected_fields = HOURLY_FIELDS

    variable_map = {
        field: idx for idx, field in enumerate(selected_fields)
    }

    df = build_dataframe(hourly, variable_map)
    df = add_date_time_columns(df)

    field_map = {
        "date": "date",
        "time": "time",
        **{k: k for k in selected_fields}
    }

    return map_to_models(
        df,
        HourlyRecord,
        field_map,
        float_fields=set(selected_fields)
    )

def _build_daily_records(daily) -> list[DailyRecord]:
    selected_fields = DAILY_FIELDS

    variable_map = {
        field: idx for idx, field in enumerate(selected_fields)
    }

    df = build_dataframe(daily, variable_map)
    df = add_date_time_columns(df)

    field_map = {
        "date": "date",
        "time": "time",
        **{k: k for k in selected_fields}
    }

    return map_to_models(
        df,
        DailyRecord,
        field_map,
        float_fields=set(selected_fields)
    )

# main functions to get forecast and historical weather, with options for hourly and daily
def get_forecast_weather_hourly(latitude: float, longitude: float, forecast_days: int):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": list(HOURLY_FIELDS),
        "temperature_unit": "fahrenheit",
        "forecast_days": forecast_days,
    }

    responses = openmeteo_client.weather_api(
        url,
        params=params
    )

    response = responses[0]
    hourly = response.Hourly()
    records = _build_hourly_records(hourly)

    return {"hourly": records}


def get_forecast_weather_daily(latitude: float, longitude: float, forecast_days: int):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": list(DAILY_FIELDS),
        "temperature_unit": "fahrenheit",
        "forecast_days": forecast_days,
    }

    responses = openmeteo_client.weather_api(
        url,
        params=params
    )

    response = responses[0]
    daily = response.Daily()
    records = _build_daily_records(daily)
    return {"daily": records}

# get the historical weather but daily and hourly, with start_date and end_date params
def get_historical_weather_hourly(latitude: float, longitude: float, start_date: str, end_date: str):
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": list(HOURLY_FIELDS),
        "temperature_unit": "fahrenheit",
    }

    responses = openmeteo_client.weather_api(
        url,
        params=params
    )

    response = responses[0]
    hourly = response.Hourly()

    records = _build_hourly_records(hourly)
    return {"hourly": records}

def get_historical_weather_daily(latitude: float, longitude: float, start_date: str, end_date: str):
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": list(DAILY_FIELDS),
        "temperature_unit": "fahrenheit",
    }

    responses = openmeteo_client.weather_api(
        url,
        params=params
    )

    response = responses[0]
    daily = response.Daily()

    records = _build_daily_records(daily)
    return {"daily": records}
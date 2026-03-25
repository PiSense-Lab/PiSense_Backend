import pandas as pd
from pisense.backend.models.weather_models import HOURLY_VARIABLES, DAILY_VARIABLES, HourlyRecord, DailyRecord
from pisense.backend.clients.openmeteo_client import openmeteo_client
from pisense.backend.utils.weather_utils import map_to_models, add_date_time_columns, build_dataframe


def _build_hourly_records(hourly, selected_fields) -> list[HourlyRecord]:
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

def _build_daily_records(daily, selected_fields) -> list[DailyRecord]:
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
        float_fields=set(selected_fields) - {"sunrise", "sunset"},
        datetime_fields={"sunrise", "sunset"} & set(selected_fields)
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
# GET /get-forecast-weather?
# latitude=44.8&
# longitude=-91.5&
# temperature_2m=true&
# precipitation=true&
# uv_index_max=true
def get_weather_forecast(
    latitude,
    longitude,
    forecast_days=7,
    hourly_fields=None,
    daily_fields=None
):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "forecast_days": forecast_days,
        "wind_speed_unit": "mph",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
    }

    if hourly_fields:
        params["hourly"] = hourly_fields

    if daily_fields:
        params["daily"] = daily_fields

    responses = openmeteo_client.weather_api(
        "https://api.open-meteo.com/v1/forecast",
        params=params
    )

    response = responses[0]

    result = {}

    if hourly_fields:
        result["hourly"] = _build_hourly_records(response.Hourly(), hourly_fields)

    if daily_fields:
        result["daily"] = _build_daily_records(response.Daily(), daily_fields)

    return result
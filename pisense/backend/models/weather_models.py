from pydantic import BaseModel
from datetime import date, datetime, time

HOURLY_VARIABLES = {
    "temperature_2m": 0,
    "showers": 1,
    "rain": 2,
    "precipitation": 3,
    "precipitation_probability": 4,
    "apparent_temperature": 5,
    "dew_point_2m": 6,
    "relative_humidity_2m": 7,
    "snowfall": 8,
    "snow_depth": 9,
}

DAILY_VARIABLES = {
    "temperature_2m_max": 0,
    "temperature_2m_min": 1,
    "apparent_temperature_max": 2,
    "apparent_temperature_min": 3,
    "daylight_duration": 4,
    "uv_index_max": 5,
}

FIELD_TYPES = {
    "temperature_2m": float,
}

ALL_HOURLY = set(HOURLY_VARIABLES.keys())
ALL_DAILY = set(DAILY_VARIABLES.keys())

class HourlyRecord(BaseModel):
    date: date
    time: time

    # temperature-related
    temperature_2m: float | None = None
    apparent_temperature: float | None = None
    dew_point_2m: float | None = None

    # precipitation
    precipitation: float | None = None
    rain: float | None = None
    showers: float | None = None
    snowfall: float | None = None
    snow_depth: float | None = None

    # probability / humidity
    precipitation_probability: float | None = None
    relative_humidity_2m: float | None = None


class DailyRecord(BaseModel):
    date: date
    time: time  # optional but consistent with your pipeline

    # temperature
    temperature_2m_max: float | None = None
    temperature_2m_min: float | None = None
    apparent_temperature_max: float | None = None
    apparent_temperature_min: float | None = None

    # solar
    daylight_duration: float | None = None  # seconds

    # UV
    uv_index_max: float | None = None


class WeatherResponse(BaseModel):
    hourly: list[HourlyRecord] | None = None
    daily: list[DailyRecord] | None = None

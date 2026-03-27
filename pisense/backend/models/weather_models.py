from pydantic import BaseModel
from datetime import date, time

from typing import Literal

ForecastType = Literal["hourly", "daily"]
# these are the fields we want to extract from the API, and they also correspond to the fields in our Pydantic models
HOURLY_FIELDS = [
    "temperature_2m",
    "showers",
    "rain",
    "precipitation",
    "precipitation_probability",
    "apparent_temperature",
    "dew_point_2m",
    "relative_humidity_2m",
    "snowfall",
    "snow_depth",
]

DAILY_FIELDS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "daylight_duration",
    "uv_index_max",
]
# these are the Pydantic models for the hourly and daily records, and the response model that contains both
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

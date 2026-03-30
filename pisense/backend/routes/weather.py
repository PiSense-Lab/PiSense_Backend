from datetime import date

from fastapi import APIRouter, Request
from pisense.backend.models.weather_models import WeatherResponse, ForecastType
from pisense.backend.services.weather_service import (
    get_forecast_weather_daily,
    get_forecast_weather_hourly,
    get_historical_weather_daily,
    get_historical_weather_hourly,

)

router = APIRouter(prefix="/weather")

# to use /weather/forecast-weather?type=hourly&latitude=40.7&longitude=-74.0&forecast_days=14
# @router.get(
#     "/forecast-weather",
#     response_model=WeatherResponse
# )
# async def weather_forecast(type: ForecastType = "hourly", latitude: float = 46.73, longitude: float = 94.69, forecast_days: int = 7):
#     if type == "hourly":
#         return get_forecast_weather_hourly(latitude=latitude, longitude=longitude, forecast_days=forecast_days)
#     else:
#         return get_forecast_weather_daily(latitude=latitude, longitude=longitude, forecast_days=forecast_days)

@router.get(
    "/forecast-weather/hourly",
    response_model=WeatherResponse
)
async def forecast_weather_hourly(
    latitude: float = 46.73,
    longitude: float = 94.69,
    forecast_days: int = 7
):
    return get_forecast_weather_hourly(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days
    )

@router.get(
    "/forecast-weather/daily",
    response_model=WeatherResponse
)
async def forecast_weather_daily(
    latitude: float = 46.73,
    longitude: float = 94.69,
    forecast_days: int = 7
):
    return get_forecast_weather_daily(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days
    )

# @router.get(
#     "/historical-weather",
#     response_model=WeatherResponse
# )
# # historical weather has option for "start_date": "2022-01-01",	"end_date": "2022-12-31",
# async def historical_weather(type: ForecastType = "hourly", latitude: float = 46.73, longitude: float = 94.69, start_date: date = date(2025, 1, 1), end_date: date = date(2025, 12, 31)):
#     if type == "hourly":
#         return get_historical_weather_hourly(latitude=latitude, longitude=longitude, start_date=start_date, end_date=end_date)
#     else:
#         return get_historical_weather_daily(latitude=latitude, longitude=longitude, start_date=start_date, end_date=end_date)

@router.get(
    "/historical-weather/hourly",
    response_model=WeatherResponse
)
async def historical_weather_hourly(
    latitude: float = 46.73,
    longitude: float = 94.69,
    start_date: date = date(2025, 1, 1),
    end_date: date = date(2025, 12, 31)
):
    return get_historical_weather_hourly(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date
    )

@router.get(
    "/historical-weather/daily",
    response_model=WeatherResponse
)
async def historical_weather_daily(
    latitude: float = 46.73,
    longitude: float = 94.69,
    start_date: date = date(2025, 1, 1),
    end_date: date = date(2025, 12, 31)
):
    return get_historical_weather_daily(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date
    )

from fastapi import APIRouter
from pisense.backend.models.weather_models import HourlyRecord, DailyRecord
from pisense.backend.services.weather_service import (
    get_forecast_day_weather,
    get_forecast_weather,
    get_historical_weather
)

router = APIRouter(prefix="/weather")

# to use /weather/forecast-weather?latitude=40.7&longitude=-74.0&forecast_days=14
@router.get(
    "/forecast-weather",
    response_model=list[HourlyRecord]
)
async def weather_forecast(latitude: float = 46.73, longitude: float = 94.69, forecast_days: int = 7):
    return get_forecast_weather(latitude=latitude, longitude=longitude, forecast_days=forecast_days)


@router.get(
    "/historical-weather",
    response_model=list[HourlyRecord]
)
async def historical_weather():
    return get_historical_weather()


@router.get(
    "/daily-weather",
    response_model=list[DailyRecord]
)
async def daily_weather(latitude: float = 46.73, longitude: float = 94.69):
    return get_forecast_day_weather(latitude=latitude, longitude=longitude)

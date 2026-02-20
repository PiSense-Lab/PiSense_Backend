from fastapi import APIRouter
from pisense.backend.models.weather_models import HourlyRecord, DailyRecord
from pisense.backend.services.weather_service import (
    get_forecast_day_weather,
    get_forecast_weather,
    get_historical_weather
)

router = APIRouter()


@router.get(
    "/weather",
    response_model=list[HourlyRecord]
)
async def weather_forecast():
    return get_forecast_weather()


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
async def daily_weather():
    return get_forecast_day_weather()

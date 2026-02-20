from fastapi import APIRouter
from pisense.api.models.weather_models import HourlyRecord
from pisense.api.services.weather_service import (
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

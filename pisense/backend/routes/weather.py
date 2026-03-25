from fastapi import APIRouter, Request
from pisense.backend.models.weather_models import HourlyRecord, DailyRecord, WeatherResponse
from pisense.backend.services.weather_service import (
    get_forecast_weather_daily,
    get_forecast_weather_hourly,
    get_historical_weather,
    get_weather_forecast
)
from pisense.backend.utils.weather_utils import extract_fields

router = APIRouter(prefix="/weather")

# to use /weather/forecast-weather?type=hourly&latitude=40.7&longitude=-74.0&forecast_days=14
@router.get(
    "/forecast-weather",
    response_model=list[HourlyRecord]
)
async def weather_forecast(type: str = "hourly", latitude: float = 46.73, longitude: float = 94.69, forecast_days: int = 7):
    if type == "hourly":
        return get_forecast_weather_hourly(latitude=latitude, longitude=longitude, forecast_days=forecast_days)
    else:
        return get_forecast_weather_daily(latitude=latitude, longitude=longitude, forecast_days=forecast_days)

@router.get(
    "/historical-weather",
    response_model=list[HourlyRecord]
)
# historical weather has option for "start_date": "2022-01-01",	"end_date": "2022-12-31",
async def historical_weather(latitude: float = 46.73, longitude: float = 94.69, start_date: str = "2025-01-01", end_date: str = "2025-12-31"):
    return get_historical_weather(latitude=latitude, longitude=longitude, start_date=start_date, end_date=end_date)

@router.get("/get-forecast-weather", response_model=WeatherResponse)
async def get_forecast_weather(
    request: Request,
    latitude: float = 46.73,
    longitude: float = 94.69,
    forecast_days: int = 7
):
    query_params = dict(request.query_params)

    hourly_fields, daily_fields = extract_fields(query_params)

    return get_weather_forecast(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days,
        hourly_fields=hourly_fields,
        daily_fields=daily_fields
    )
from fastapi import FastAPI
import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from pydantic import BaseModel # for data validation(?)
from datetime import datetime

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Amber just messing around (2/18)

@app.get("/weather")
async def get_weather_forecast():
    
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 46.73,
        "longitude": 94.69,
        "hourly": ["temperature_2m", "precipitation", "wind_speed_10m"],
        "current": ["temperature_2m", "relative_humidity_2m"],
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    data = pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )
    # is hourly data a dictionary 
    hourly_data = pd.DataFrame({
        "date": data,
        "temperature_2m": hourly_temperature_2m
    })

    records = [
        HourlyRecord(
            date=row.date.to_pydatetime(),
            temperature_2m=float(row.temperature_2m)
        )
        for row in hourly_data.itertuples(index=False)
    ]
    
    return records

class HourlyRecord(BaseModel):
    date: datetime
    temperature_2m: float

@app.get(
        "/get_historical_weather_data", 
        response_model=list[HourlyRecord]
)
async def get_historical_weather_data():
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 46.73,
        "longitude": 94.69,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "hourly": "temperature_2m",
        "wind_speed_unit": "mph",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    # print(f"Elevation: {response.Elevation()} m asl")
    # print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    data = pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )
    # is hourly data a dictionary 
    hourly_data = pd.DataFrame({
        "date": data,
        "temperature_2m": hourly_temperature_2m
    })

    records = [
        HourlyRecord(
            date=row.date.to_pydatetime(),
            temperature_2m=float(row.temperature_2m)
        )
        for row in hourly_data.itertuples(index=False)
    ]
    
    return records
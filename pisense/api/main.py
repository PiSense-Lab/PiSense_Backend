from fastapi import FastAPI
from pisense.api.routes.weather import router as weather_router

# to start server: source .venv/bin/activate (pisense-backend) kuhna4273@eStout-G418107M:~/PiSense/PiSense_Backend$ fastapi dev pisense/api/main.py

app = FastAPI()

app.include_router(weather_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
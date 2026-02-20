from fastapi import FastAPI
from pisense.api.routes.weather import router as weather_router

# to start server: source .venv/bin/activate && fastapi dev pisense/api/main.py

app = FastAPI()

app.include_router(weather_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

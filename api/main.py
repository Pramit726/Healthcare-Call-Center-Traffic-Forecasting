from fastapi import FastAPI

from .routers import forecast, home

app = FastAPI()

app.include_router(home.router)
app.include_router(forecast.router)

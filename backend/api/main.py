from fastapi import FastAPI

from api.routers.health import router as health_router
from api.routers.lines import router as lines_router
from api.routers.routes import router as routes_router
from api.routers.stops import router as stops_router
from api.routers.vehicles import router as vehicles_router

app = FastAPI(title="WroTransit API")
app.include_router(health_router)
app.include_router(stops_router)
app.include_router(lines_router)
app.include_router(routes_router)
app.include_router(vehicles_router)

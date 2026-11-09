from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers.health import router as health_router
from api.routers.routes import router as routes_router
from api.routers.shapes import router as shapes_router
from api.routers.stops import router as stops_router
from api.routers.vehicles import router as vehicles_router

app = FastAPI(title="WroTransit API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(stops_router)
app.include_router(routes_router)
app.include_router(shapes_router)
app.include_router(vehicles_router)

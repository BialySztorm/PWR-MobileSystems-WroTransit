import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.schemas.shape import ShapeRead

router = APIRouter(prefix="/shapes", tags=["shapes"])


@router.get("", response_model=list[ShapeRead])
def list_shapes(
    bbox: str = Query(..., description="minLon,minLat,maxLon,maxLat (map viewport)"),
    db: Session = Depends(get_db),
) -> list[dict]:
    min_lon, min_lat, max_lon, max_lat = (float(v) for v in bbox.split(","))
    stmt = text(
        """
        SELECT DISTINCT ON (s.shape_id) s.shape_id, ST_AsGeoJSON(s.geom) AS geojson, r.type AS route_type
        FROM shapes s
        LEFT JOIN trips t ON t.shape_id = s.shape_id
        LEFT JOIN routes r ON r.route_id = t.route_id
        WHERE ST_Intersects(s.geom, ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326))
        LIMIT 300
        """
    )
    rows = db.execute(
        stmt, {"min_lon": min_lon, "min_lat": min_lat, "max_lon": max_lon, "max_lat": max_lat}
    )
    return [
        {
            "shape_id": row.shape_id,
            "coordinates": json.loads(row.geojson)["coordinates"],
            "route_type": row.route_type,
        }
        for row in rows
    ]

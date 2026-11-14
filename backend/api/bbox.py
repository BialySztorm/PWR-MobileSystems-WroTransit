from fastapi import HTTPException


def parse_bbox(bbox: str) -> tuple[float, float, float, float]:
    """Parses a "minLon,minLat,maxLon,maxLat" map viewport string, raising a clean 422
    instead of letting a malformed value surface as an uncaught 500."""
    parts = bbox.split(",")
    if len(parts) != 4:
        raise HTTPException(
            status_code=422, detail="bbox must be 'minLon,minLat,maxLon,maxLat'"
        )
    try:
        return tuple(float(v) for v in parts)  # type: ignore[return-value]
    except ValueError:
        raise HTTPException(
            status_code=422, detail="bbox must be 'minLon,minLat,maxLon,maxLat'"
        ) from None

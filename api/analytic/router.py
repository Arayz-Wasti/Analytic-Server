from datetime import datetime, timedelta
from typing import Literal
from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    BackgroundTasks
)
from backend.api.analytic.analytic_service import AnalyticsService
from backend.api.analytic.schemas.request import (
    EventCreate,
    Event,
    Metric
)
from backend.utils.auth import JWTBearer
from datetime import timezone
from backend.utils.mongodb import get_db
import os

router = APIRouter()


@router.get("/events/timeseries")
async def events_timeseries(
    interval: str = Query("day", pattern="^(day|hour)$"),
    days: int = Query(7, ge=1, le=90),
    token: str = Depends(JWTBearer()),
    db=Depends(get_db)
):
    """
    Time-series analytics
    """
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    return await AnalyticsService.events_timeseries(
        interval,
        start,
        end,
        db
    )

@router.get("/events/grouped")
async def events_grouped(
    by: Literal["event_name", "event_category", "source"] = Query(
            ...,
            description="Field to group events by",
            example="event_name"
        ),
    token: str = Depends(JWTBearer()),
    db=Depends(get_db)
):
    """
    Group events by field
    """
    return await AnalyticsService.events_grouped_by(by, db)

@router.get("/events/count")
async def get_count_events(token: str = Depends(JWTBearer()), db=Depends(get_db)):
    try:
        filters = {"created_at": {"$gte": datetime.now(timezone.utc) - timedelta(days=1)}}
        count = await AnalyticsService.count_events(filters, db)
        return {"count": count}
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}

@router.get("/events/daily")
async def daily_events(token: str = Depends(JWTBearer()), db = Depends(get_db)):
    today = datetime.utcnow() - timedelta(days=1)
    filters = {"created_at": {"$gte": today}}
    count = await AnalyticsService.daily_events(filters,db)
    return {"daily_events": count}


@router.post("/events", status_code=202)
async def create_event(
    payload: EventCreate,
    background_tasks: BackgroundTasks,
    token: str = Depends(JWTBearer()),
    db=Depends(get_db)
):
    """
    Track analytics event (async background ingestion)
    """
    event = Event(**payload.model_dump())
    background_tasks.add_task(
        AnalyticsService.create_event, event, db
    )
    return {
        "status": "accepted",
        "message": "Event queued for ingestion"
    }


@router.get("/events")
async def list_events(
    event_name: str | None = None,
    user_id: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    token: str = Depends(JWTBearer()),
    db=Depends(get_db)
):
    """
    List events with filters & pagination
    """
    return await AnalyticsService.list_events(
        event_name,
        user_id,
        start_date,
        end_date,
        page,
        limit,
        db
    )


@router.get("/events/{event_id}")
async def get_event(event_id: str, token: str = Depends(JWTBearer()), db=Depends(get_db)):
    """
    Get single event by ID
    """
    event = await AnalyticsService.get_event(event_id, db)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/users/active")
async def active_users(
    range: str = Query("day", pattern="^(day|week|month)$"),
    token: str = Depends(JWTBearer()),
    db=Depends(get_db)
):
    """
    Active users (DAU / WAU / MAU)
    """
    now = datetime.utcnow()
    delta = {
        "day": timedelta(days=1),
        "week": timedelta(days=7),
        "month": timedelta(days=30)
    }
    start = now - delta[range]
    count = await AnalyticsService.active_users(start, db)
    return {
        "range": range,
        "active_users": count
    }


@router.post("/metrics", status_code=201)
async def create_metric(
    payload: Metric,
    background_tasks: BackgroundTasks,
    token: str = Depends(JWTBearer()),
    db=Depends(get_db)
):
    """
    Track custom metric
    """
    metric = Metric(**payload.model_dump())
    background_tasks.add_task(
        AnalyticsService.create_metric, metric, db
    )
    return {
        "status": "accepted",
        "message": "Metric queued for ingestion"
    }


@router.get("/metrics/weather")
async def fetch_weather(city: str, token: str = Depends(JWTBearer()), db=Depends(get_db)):
    """
   Fetch weather metric from OpenWeatherMap API and store it.
    """
    endpoint = "https://api.openweathermap.org/data/2.5/weather"
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    params = {"q": city, "appid": api_key, "units": "metric"}
    metric = await AnalyticsService.track_third_party_metric(
        name="temperature",
        endpoint=endpoint,
        params=params,
        db=db,
        extract_path=["main", "temp"],
        source="openweathermap"
    )

    return {"status": "success", "metric": metric}
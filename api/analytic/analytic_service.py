from datetime import datetime, timedelta, timezone
from bson import ObjectId
from backend.utils.aiohttp_client import aiohttp_client_session
import logging

from backend.utils.semaphore import semaphore

log = logging.getLogger("analytic_server")

class AnalyticsService:
    """
    Business logic layer for analytics events & metrics
    """

    @staticmethod
    async def daily_events(filters: dict, db):
        return await db.event.count_documents(filters)

    @staticmethod
    async def create_event(event, db):
        data = event.model_dump()
        data["created_at"] = datetime.utcnow()

        result = await db.event.insert_one(data)
        return {"event_id": str(result.inserted_id)}

    @staticmethod
    async def list_events(
        event_name: str | None,
        user_id: str | None,
        start_date: datetime | None,
        end_date: datetime | None,
        page: int,
        limit: int,
        db
    ):
        query = {}
        if event_name:
            query["event_name"] = event_name
        if user_id:
            query["user_id"] = user_id
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        cursor = (
            db.event
            .find(query)
            .sort("created_at", -1)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        events = await cursor.to_list(length=limit)
        for e in events:
            e["_id"] = str(e["_id"])
        return events

    @staticmethod
    async def get_event(event_id: str, db):
        event = await db.event.find_one({"_id": ObjectId(event_id)})
        if not event:
            return None
        event["_id"] = str(event["_id"])
        return event

    @staticmethod
    async def count_events(filters: dict, db):
        return await db.event.count_documents(filters)

    @staticmethod
    async def events_grouped_by(field: str, db):
        allowed_fields = {"event_name", "event_category", "source"}
        if field not in allowed_fields:
            raise ValueError(f"Invalid grouping field: {field}")
        pipeline = [
            {
                "$group": {
                    "_id": f"${field}",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ]
        results = await db.event.aggregate(pipeline).to_list(length=None)
        return [
            {
                "key": r["_id"] or "unknown",
                "count": r["count"]
            }
            for r in results
        ]

    @staticmethod
    async def events_timeseries(interval: str, start: datetime, end: datetime, db):
        group_format = "%Y-%m-%d" if interval == "day" else "%Y-%m-%d %H"
        pipeline = [
            {"$match": {"created_at": {"$gte": start, "$lte": end}}},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": group_format,
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]

        results = await db.event.aggregate(pipeline).to_list(length=None)
        return results


    @staticmethod
    async def active_users(start: datetime, db):
        pipeline = [
            {"$match": {"created_at": {"$gte": start}}},
            {"$group": {"_id": "$user_id"}},
            {"$count": "active_users"}
        ]

        result = await db.event.aggregate(pipeline).to_list(length=1)
        return result[0]["active_users"] if result else 0

    @staticmethod
    async def create_metric(metric, db):
        data = metric.model_dump()
        data["created_at"] = datetime.utcnow()
        result = await db.metric.insert_one(data)
        return {"metric_id": str(result.inserted_id)}

    @staticmethod
    async def fetch_external_metric(
            endpoint: str,
            params: dict | None = None,
            headers: dict | None = None
    ) -> dict:

        await aiohttp_client_session.create()

        try:
            async with semaphore:
                response = await aiohttp_client_session.request(
                    method="GET",
                    url=endpoint,
                    headers=headers,
                    params=params
                )

                if response.status == 401:
                    body = await response.text()
                    log.error(f"Invalid API key for {endpoint}: {body}")
                    raise RuntimeError("Third-party API authentication failed")

                if response.status >= 400:
                    body = await response.text()
                    raise RuntimeError(f"External API error {response.status}: {body}")

                data = await response.json()
                log.info(f"Fetched external metric from {endpoint}")
                return data

        except Exception as e:
            log.error(f"Error fetching external metric: {e}")
            raise

    @staticmethod
    async def track_third_party_metric(
            name: str,
            endpoint: str,
            params: dict,
            db,
            extract_path: list[str] | None = None,
            source: str = "third_party"
    ):
        """
        Fetch a metric from an external API, extract a value, and store it.
        `extract_path` is a list of keys to navigate nested JSON.
        """
        data = await AnalyticsService.fetch_external_metric(endpoint, params)
        value = data
        if extract_path:
            try:
                for key in extract_path:
                    value = value[key]
            except (KeyError, TypeError):
                value = None
        if value is None:
            value = 1
        metric_doc = {
            "metric_name": name,
            "value": value,
            "source": source,
            "fetched_at": datetime.now(timezone.utc),
            "raw_response": data
        }
        result = await db.metric.insert_one(metric_doc)
        return {"metric_id": str(result.inserted_id), "value": value, "source": source}

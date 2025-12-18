async def create_analytics_indexes(db):
    await db.event.create_index("created_at")
    await db.event.create_index("event_name")
    await db.event.create_index("event_category")
    await db.event.create_index("user_id")
    await db.event.create_index(
        [("event_name", 1), ("created_at", -1)]
    )

    await db.metric.create_index("created_at")

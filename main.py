import asyncio
from fastapi import FastAPI, Depends, Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.api.user.router import router as user
from backend.api.analytic.router import router as analytic
from backend.api.email_service.router import router as email
import json_logging
import time
import socket
import logging
from backend.utils.aiohttp_client import aiohttp_client_session
from backend.utils.mongodb import connect_to_mongo, close_mongo, get_db
from contextlib import asynccontextmanager
from backend.utils.mongodb_indexes import create_analytics_indexes

json_logging.init_fastapi(enable_json=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo()

app = FastAPI(
    title="Analytics Server",
    lifespan=lifespan,
    description="API for Analytics Server",
    swagger_ui_parameters={"defaultModelsExpandDepth":-1},
    version="1.0",
    redoc_url=None,
)

json_logging.init_request_instrument(app)

service_start_time = ""
version:str = "unknown"
branch:str = "unknown"
server_hostname:str = socket.gethostname()

log = logging.getLogger("analytic_server")

async def app_startup():
    global service_start_time
    service_start_time = time.time()
    await aiohttp_client_session.create()
    db = await get_db()
    await create_analytics_indexes(db)
    await connect_to_mongo()
    log.info(" Analytics Server STARTED", extra={
        "hostname": server_hostname,
        "startup_time": service_start_time
    })


async def app_shutdown():
    await asyncio.sleep(1)
    await aiohttp_client_session.close()
    await close_mongo()
    log.info("Analytics Server SHUTTING DOWN")


async def capture_body(request: Request):
    request.state.request_body = {}
    try:
        request.state.request_body = await request.json()
    except Exception:
        pass



class CaptureRequestBodyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            request.state.request_body = await request.json()
        except Exception:
            request.state.request_body = {}
        response = await call_next(request)
        return response


app.include_router(user,
                   prefix="/api/user",
                   tags=["user"],
                   dependencies=[Depends(capture_body)])
app.include_router(analytic,
                   prefix="/api/analytics",
                   tags=["analytics"]
                   )

app.include_router(email,
                   prefix="/api/email",
                   tags=["email"])

app.add_middleware(CaptureRequestBodyMiddleware)
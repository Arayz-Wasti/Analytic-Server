import aiohttp
import asyncio
import logging
from typing import Optional, Any, Dict
import time

log = logging.getLogger("analytics.http")


class HttpClientConfig:
    TIMEOUT_TOTAL = 10
    TIMEOUT_CONNECT = 3
    TIMEOUT_READ = 5

    MAX_CONNECTIONS = 100
    DNS_CACHE_TTL = 300

    DEFAULT_HEADERS = {
        "Content-Type": "application/json",
        "User-Agent": "analytics-server/1.0"
    }

    SHUTDOWN_TIMEOUT = 5
    RETRIES = 3
    RETRY_BACKOFF = 2  # exponential


class AioHttpClientSession:
    """
    Enterprise-grade aiohttp session manager.
    """

    _session: Optional[aiohttp.ClientSession] = None
    _lock = asyncio.Lock()
    _created_at: float | None = None

    @classmethod
    async def create(cls) -> None:
        async with cls._lock:
            if cls._session and not cls._session.closed:
                log.debug("aiohttp session already initialized")
                return

            timeout = aiohttp.ClientTimeout(
                total=HttpClientConfig.TIMEOUT_TOTAL,
                connect=HttpClientConfig.TIMEOUT_CONNECT,
                sock_read=HttpClientConfig.TIMEOUT_READ
            )

            connector = aiohttp.TCPConnector(
                limit=HttpClientConfig.MAX_CONNECTIONS,
                ttl_dns_cache=HttpClientConfig.DNS_CACHE_TTL,
                enable_cleanup_closed=True
            )

            cls._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=HttpClientConfig.DEFAULT_HEADERS,
                connector=connector,
                raise_for_status=False
            )

            cls._created_at = time.time()

            log.info(
                "aiohttp session created",
                extra={
                    "connections": HttpClientConfig.MAX_CONNECTIONS,
                    "timeout": HttpClientConfig.TIMEOUT_TOTAL
                }
            )

    @classmethod
    def get(cls) -> aiohttp.ClientSession:
        if not cls._session or cls._session.closed:
            raise RuntimeError(
                "HTTP client session is not available. "
                "Ensure create() is called on startup."
            )
        return cls._session

    @classmethod
    async def close(cls) -> None:
        async with cls._lock:
            if cls._session and not cls._session.closed:
                log.info("Closing aiohttp session")

                try:
                    await asyncio.wait_for(
                        cls._session.close(),
                        timeout=HttpClientConfig.SHUTDOWN_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    log.error("Timeout while closing aiohttp session")

                cls._session = None
                cls._created_at = None

                log.info("aiohttp session closed")

    # -------------------------
    # Request Wrapper
    # -------------------------
    @classmethod
    async def request(
        cls,
        method: str,
        url: str,
        *,
        retries: int = HttpClientConfig.RETRIES,
        headers: Dict[str, str] | None = None,
        **kwargs: Any
    ) -> aiohttp.ClientResponse:

        session = cls.get()
        merged_headers = {**HttpClientConfig.DEFAULT_HEADERS, **(headers or {})}

        for attempt in range(1, retries + 1):
            try:
                start = time.time()

                response = await session.request(
                    method=method,
                    url=url,
                    headers=merged_headers,
                    **kwargs
                )

                duration = round(time.time() - start, 3)

                log.info(
                    "HTTP request completed",
                    extra={
                        "method": method,
                        "url": url,
                        "status": response.status,
                        "duration": duration
                    }
                )

                return response

            except Exception as exc:
                log.warning(
                    "HTTP request failed",
                    extra={
                        "method": method,
                        "url": url,
                        "attempt": attempt,
                        "error": str(exc)
                    }
                )

                if attempt >= retries:
                    raise

                await asyncio.sleep(HttpClientConfig.RETRY_BACKOFF ** attempt)

    # -------------------------
    # Health Check
    # -------------------------
    @classmethod
    def health(cls) -> dict:
        return {
            "session_active": cls._session is not None and not cls._session.closed,
            "created_at": cls._created_at
        }

aiohttp_client_session = AioHttpClientSession()

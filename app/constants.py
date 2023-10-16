from pathlib import Path

from redis.asyncio import Redis


SUBMISSIONS_PATH = Path("submissions")


class Connections:
    """Manage connections to external/internal services."""
    REDIS = Redis.from_url("redis://localhost")

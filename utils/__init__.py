from typing import Literal, Optional
from dataclasses import dataclass
import os
import upstash_redis
from dotenv import load_dotenv

load_dotenv()

redis = upstash_redis.Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL") or '',
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN") or ''
)

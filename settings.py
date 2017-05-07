# example

import logging
import uuid

import redis

HEARTBEAT_RATE = 3  # seconds
HEARTBEAT_CHECK_RATE = HEARTBEAT_RATE + 2

redis_client = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=7,
    charset="utf-8",
    decode_responses=True
)

logging.basicConfig(level=logging.INFO)

PROCESS_ID = uuid.uuid4()

PROVIDER_URL = 'http://blank.org/'

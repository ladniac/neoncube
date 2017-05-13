# example

import logging
import uuid

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 7

HEARTBEAT_RATE = 3  # seconds
HEARTBEAT_CHECK_RATE = HEARTBEAT_RATE + 2

logging.basicConfig(level=logging.INFO)

PROCESS_ID = str(uuid.uuid4())

PROVIDER_URL = 'http://blank.org/'

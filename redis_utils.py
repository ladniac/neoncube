import aioredis

from settings import REDIS_HOST, REDIS_PORT, REDIS_DB

lua_check_lock = (
    "local process_id = ARGV[1] "
    "local hb_check_rate = tonumber(ARGV[2]) "
    "local heartbeat = redis.call('GET', 'heartbeat') "
    "if (not heartbeat or heartbeat == process_id) then "
    "  redis.call('SETEX', 'heartbeat', hb_check_rate, process_id) "
    "  redis.call('SETEX', 'node:' .. process_id, hb_check_rate, 1) "
    "  return 1 "
    "else return 0 end"
)

lua_setnxex = (
    "local expire = ARGV[1] "
    "local rsp = redis.call('SETNX', KEYS[1], '1') "
    "if rsp == 1 then redis.call('EXPIRE', KEYS[1], expire) end "
    "return rsp"
)


async def get_redis_connection():
    conn = await aioredis.create_redis(
        (REDIS_HOST, REDIS_PORT), db=REDIS_DB
    )
    return conn

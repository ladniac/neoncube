from asyncio import get_event_loop, ensure_future, sleep

from redis.exceptions import ConnectionError
from settings import (
    HEARTBEAT_RATE, HEARTBEAT_CHECK_RATE, PROCESS_ID,
    logging, redis_client,
)
from communicator import HttpCommunicator

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
check_lock = redis_client.register_script(lua_check_lock)


def main():
    node_allowed = redis_client.set(
        'node:' + str(PROCESS_ID), 1, nx=True, ex=HEARTBEAT_CHECK_RATE)
    if not node_allowed:
        raise Exception(
            'Cannot start node. '
            f'Node identifier {PROCESS_ID} is already used by a different node'
        )
    loop = get_event_loop()
    ensure_future(heartbeat(loop))

    # Start other tasks here ...
    # (will continue to work after communicator dies)

    loop.run_forever()


async def heartbeat(loop):
    communicator = HttpCommunicator(loop)
    while True:
        logging.info('heartbeat')
        try:
            node_allowed = check_lock(args=[PROCESS_ID, HEARTBEAT_CHECK_RATE])
        except ConnectionError:
            logging.error('redis connection error')
        else:
            if node_allowed and not communicator.on:
                logging.info('communicator started')
                communicator.start()
            if not node_allowed and communicator.on:
                logging.info('communicator stopped')
                communicator.stop()
            if communicator.exception:
                logging.error(communicator.exception)
                if communicator.check_if_should_recover():
                    communicator.start()
                else:
                    return
        await sleep(HEARTBEAT_RATE)


if __name__ == '__main__':
    main()

from asyncio import get_event_loop, ensure_future, sleep

from communicator import HttpCommunicator
from redis_utils import get_redis_connection, lua_setnxex, lua_check_lock
from settings import (
    HEARTBEAT_RATE, HEARTBEAT_CHECK_RATE, PROCESS_ID,
    logging,
)


def main():
    loop = get_event_loop()
    loop.run_until_complete(check_if_node_is_allowed())
    ensure_future(heartbeat(loop))

    # Start other tasks here ...
    # (will continue to work after communicator dies)

    loop.run_forever()


async def check_if_node_is_allowed():
    redis_client = await get_redis_connection()
    node_allowed = await redis_client.eval(
        lua_setnxex,
        keys=['node:' + str(PROCESS_ID)],
        args=[HEARTBEAT_RATE]
    )
    redis_client.close()
    if not node_allowed:
        raise Exception(
            'Cannot start node. '
            f'Node identifier {PROCESS_ID} is already used by a different node'
        )


async def heartbeat(loop):
    communicator = HttpCommunicator(loop)
    redis_client = await get_redis_connection()
    while True:
        logging.info('heartbeat')
        try:
            node_allowed = await redis_client.eval(
                lua_check_lock,
                args=[PROCESS_ID, HEARTBEAT_CHECK_RATE]
            )
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
                    break
        await sleep(HEARTBEAT_RATE)
    redis_client.close()


if __name__ == '__main__':
    main()

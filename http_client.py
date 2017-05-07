from asyncio import sleep

import aiohttp
import async_timeout

from settings import PROVIDER_URL


async def client(self):
    counter = 0
    while True:
        if counter == 15:
            raise Exception('Oooops something went wrong ...')
        async with aiohttp.ClientSession(loop=self.loop) as session:
            status_code = await fetch(session, PROVIDER_URL)
            print(f'Provider responded with status code: {status_code}')
        counter += 1
        await sleep(1)


async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return response.status

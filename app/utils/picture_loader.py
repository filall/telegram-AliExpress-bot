import asyncio
from typing import List

import aiohttp


async def get_picture(client: aiohttp.ClientSession, picture_uri: str) -> bytes:
    if not picture_uri.startswith("http"):
        picture_uri = "http:" + picture_uri
    async with client.get(picture_uri) as response:
        return await response.read()


async def get_pictures(picture_uris: List[str]):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(10)) as client:
        tasks = [get_picture(client, uri) for uri in picture_uris]
        return await asyncio.gather(*tasks)

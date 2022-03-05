import aiohttp
import asyncio
from bs4 import BeautifulSoup


async def get_proxies(session):
    url = 'https://free-proxy-list.net/'
    async with session.get(url) as r:
        return await process_proxies(r.text())


def process_proxies(response):
    
    soup = BeautifulSoup(
        response,
        'html.parser'
    )

    
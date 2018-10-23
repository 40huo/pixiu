import asyncio

from backend import MAIN_LOOP

ARTICLE_QUEUE = asyncio.Queue(maxsize=500, loop=MAIN_LOOP)

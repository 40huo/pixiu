import asyncio
import time

from backend import CONSUME_LOOP

ARTICLE_QUEUE = asyncio.Queue(maxsize=500, loop=CONSUME_LOOP)


@asyncio.coroutine
async def consumer(queue):
    """
    消费者
    :param queue:
    :return:
    """
    while True:
        item = await queue.get()
        print(f'Consuming...{item}')
        time.sleep(2)
        queue.task_done()

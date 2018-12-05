import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler


def run():
    """
    后端爬虫入口
    :return:
    """
    loop = asyncio.get_event_loop()
    sched = AsyncIOScheduler()
    sched.start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
        sched.shutdown(wait=False)

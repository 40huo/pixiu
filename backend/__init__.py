import asyncio
import datetime
import importlib

import aiohttp
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from django.utils.dateparse import parse_datetime

from backend.pipelines import save
from utils.log import Logger

logger = Logger(__name__).get_logger()


async def refresh_task(sched):
    async with aiohttp.ClientSession() as session:
        spider_api = "http://localhost:8000/api/resource/"

        async with session.get(url=spider_api) as resp:
            result = await resp.json()
            for resource in result:
                spider_class = importlib.import_module(f'.{resource.get("spider_type").get("filename")}', package='.spiders')
                link = resource.get('link')
                gap = resource.get('refresh_gap')
                status = resource.get('refresh_status')
                last_refresh_time = parse_datetime(resource.get('last_refresh_time'))
                next_run_time = last_refresh_time + datetime.timedelta(hours=gap)
                task_id = f'{resource.get("name")}({next_run_time})'

                sched.add_job(
                    func=spider_class.get_spider(link),
                    args=None,
                    trigger='date',
                    next_run_time=max(next_run_time, datetime.datetime.now(tz=pytz.UTC)),
                    id=task_id,
                    name=resource.get("name"),
                    misfire_grace_time=600,
                    coalesce=True,
                    replace_existing=True
                )


def run():
    """
    后端爬虫入口
    :return:
    """
    loop = asyncio.get_event_loop()
    sched = AsyncIOScheduler()

    sched.add_job(
        func=refresh_task,
        args=(sched,),
        trigger='interval',
        seconds=5,
        next_run_time=datetime.datetime.now(),
        id='refresh-task'
    )
    sched.start()

    asyncio.ensure_future(save.consume(save.save_queue))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
        sched.shutdown(wait=False)


if __name__ == '__main__':
    run()

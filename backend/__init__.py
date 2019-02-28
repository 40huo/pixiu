import asyncio
import datetime
import importlib

import pytz
from apscheduler.events import EVENT_JOB_MAX_INSTANCES, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from django.utils.dateparse import parse_datetime

from backend.pipelines import save
from utils.log import Logger

logger = Logger(__name__).get_logger()


def spider_listener(event):
    """
    apscheduler事件回调
    :param event:
    :return:
    """
    if event.exception:
        logger.warning(f'任务出现异常 {event.traceback}')
    else:
        pass


async def refresh_task(sched):
    from rest_framework.test import RequestsClient

    client = RequestsClient()
    req = client.get(url='http://testserver/api/resource/')

    result = req.json()
    for resource in result:
        spider_class = importlib.import_module(f'.{resource.get("spider_type").get("filename")}', package='.spiders')
        link = resource.get('link')
        resource_id = resource.get('id')
        default_category_id = resource.get('default_category')
        default_tag_id = resource.get('default_tag')
        gap = resource.get('refresh_gap')
        status = resource.get('refresh_status')
        last_refresh_time = parse_datetime(resource.get('last_refresh_time'))
        next_run_time = last_refresh_time + datetime.timedelta(hours=gap)
        task_id = f'{resource.get("name")}({next_run_time})'

        sched.add_job(
            func=spider_class.get_spider(link, resource_id=resource_id, default_category_id=default_category_id, default_tag_id=default_tag_id),
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
    import os
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pixiu.settings")
    django.setup()

    loop = asyncio.get_event_loop()
    sched = AsyncIOScheduler()

    sched.add_listener(spider_listener, mask=EVENT_JOB_MAX_INSTANCES | EVENT_JOB_ERROR | EVENT_JOB_MISSED)

    sched.add_job(
        func=refresh_task,
        args=(sched,),
        trigger='interval',
        seconds=5,
        misfire_grace_time=600,
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

import asyncio
import concurrent.futures
import datetime
import importlib
import logging
import re
import traceback

import pytz
from apscheduler.events import EVENT_JOB_MAX_INSTANCES, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from django.utils.dateparse import parse_datetime

from backend.pipelines import save
from utils import notify
from utils.http_req import send_req
from utils.log import Logger

logger = Logger(__name__).get_logger()
logging.getLogger("apscheduler.scheduler").setLevel(logging.WARNING)
logging.getLogger("apscheduler.executors").setLevel(logging.INFO)
spider_id_re = re.compile(r'\((\d+)\)$')
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)


def spider_listener(event):
    """
    apscheduler事件回调
    :param event:
    :return:
    """
    try:
        match = spider_id_re.search(event.job_id)
        if match:
            spider_id = int(match.group(1))
            if event.code == EVENT_JOB_ERROR:
                msg = f'任务出现异常 {event.traceback}'
                logger.error(msg)
                post_data = {
                    'message': msg,
                    'level': 4,
                    'spider': spider_id
                }
            elif event.code == EVENT_JOB_MISSED:
                msg = f'任务 {event.job_id} 错过执行时间 {event.scheduled_run_time}'
                logger.warning(msg)
                post_data = {
                    'message': msg,
                    'level': 3,
                    'spider': spider_id
                }
            elif event.code == EVENT_JOB_MAX_INSTANCES:
                msg = f'任务 {event.job_id} 达到最大同时执行数量'
                logger.warning(msg)
                post_data = {
                    'message': msg,
                    'level': 3,
                    'spider': spider_id
                }
            else:
                msg = f'任务 {event.job_id} 出现未知异常'
                logger.warning(msg)
                post_data = {
                    'message': msg,
                    'level': 3,
                    'spider': spider_id
                }

            req = send_req(method='post', url='/api/spider-event/', data=post_data)
            if req.status_code == 201:
                logger.info('任务异常事件上报成功')
            else:
                logger.warning(f'任务异常时间上报失败，状态码 {req.status_code}，响应详情 {req.text}')
        else:
            logger.error(f'任务id中不存在爬虫id {event.traceback}')
            notify.send_wechat(title='Pixiu任务异常-任务id中不存在爬虫id', content=event.traceback)
            notify.send_mail(content=event.traceback, sub='Pixiu任务异常')
    except Exception as e:
        logger.error(f'处理任务异常时出错 {e}', exc_info=True)
        notify.send_wechat(title='Pixiu任务异常-处理任务异常时出错', content=traceback.format_exc())
        notify.send_mail(content=traceback.format_exc(), sub='Pixiu任务异常')


async def refresh_task(loop, scheduler):
    """
    任务获取
    :param loop: 协程loop
    :param scheduler: apscheduler
    :return:
    """
    req = await loop.run_in_executor(
        executor,
        send_req,
        'get',
        '/api/resource/'
    )
    if req.status_code != 200:
        msg = f'resource API请求失败 {req.json()}'
        logger.error(msg)
        raise Exception(msg)

    result = req.json()
    for resource in result:
        spider_class = importlib.import_module(f'.{resource.get("spider_type").get("filename")}', package='backend.spiders')
        link = resource.get('link')
        resource_id = resource.get('id')
        default_category_id = resource.get('default_category')
        default_tag_id = resource.get('default_tag')
        gap = resource.get('refresh_gap')
        status = resource.get('refresh_status')
        last_refresh_time = parse_datetime(resource.get('last_refresh_time'))

        # (0, '从未刷新过')
        # (1, '刷新失败')
        if status in (0, 1):
            next_run_time = datetime.datetime.now(tz=pytz.UTC)
        else:
            next_run_time = last_refresh_time + datetime.timedelta(hours=gap)

        task_id = f'{resource.get("name")}-({resource.get("spider_type").get("id")})'

        for job in scheduler.get_jobs():
            if job.id == task_id:
                job.modify(
                    next_run_time=max(next_run_time, datetime.datetime.now(tz=pytz.UTC))
                )
                return None

        scheduler.add_job(
            func=spider_class.get_spider(loop, link, resource_id=resource_id, default_category_id=default_category_id, default_tag_id=default_tag_id),
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
    scheduler = AsyncIOScheduler()

    scheduler.add_listener(spider_listener, mask=EVENT_JOB_MAX_INSTANCES | EVENT_JOB_ERROR | EVENT_JOB_MISSED)

    scheduler.add_job(
        func=refresh_task,
        args=(loop, scheduler),
        trigger='interval',
        seconds=5,
        misfire_grace_time=600,
        next_run_time=datetime.datetime.now(),
        id='refresh-task'
    )
    scheduler.start()

    asyncio.ensure_future(save.consume(loop, save.save_queue))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info(f'退出......')
        scheduler.shutdown(wait=False)
        loop.close()

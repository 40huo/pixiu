import asyncio
import concurrent.futures
import datetime
import importlib
import logging
import re

import pytz
from apscheduler.events import EVENT_JOB_MAX_INSTANCES, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from django.utils.dateparse import parse_datetime
from rest_framework.reverse import reverse

from backend.pipelines import save
from utils import enums
from utils.http_req import send_req
from utils.log import Logger

logger = Logger(__name__).get_logger()
logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("django.request").setLevel(logging.ERROR)
spider_id_re = re.compile(r'\((\d+),(\d+)\)$')
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
            resource_id = int(match.group(2))
            if event.code == EVENT_JOB_ERROR:
                msg = f'任务 {event.job_id} 出现异常 {event.traceback}'
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

            req = send_req(method='post', url=reverse(viewname='spider-event-list'), data=post_data)
            if req.status_code == 201:
                logger.info('任务异常事件上报成功')
            else:
                logger.warning(f'任务异常事件上报失败，状态码 {req.status_code}，响应详情 {req.text}')

            req = send_req(
                method='patch',
                url=reverse(viewname='resource-detail', args=[resource_id]),
                data={
                    'last_refresh_time': datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%S'),
                    'refresh_status': enums.ResourceRefreshStatus.FAIL.value
                }
            )
            if req.status_code == 200:
                logger.info('更新订阅源状态成功')
            else:
                logger.warning(f'更新订阅源状态失败，状态码 {req.status_code}，响应详情 {req.text}')
        else:
            logger.error(f'任务id中不存在爬虫id {event}')
    except Exception as e:
        logger.error(f'处理任务异常时出错 {e}', exc_info=True)


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
        reverse(viewname='resource-list')
    )
    if req.status_code == 200:
        logger.debug('请求/api/resource/成功')
    else:
        msg = f'resource API请求失败 {req.json()}'
        logger.error(msg)
        raise Exception(msg)

    result = req.json()
    for resource in result:
        is_enabled = resource.get('is_enabled')
        if not is_enabled:
            continue

        spider_class = importlib.import_module(f'.{resource.get("spider_type").get("filename")}', package='backend.spiders')
        link = resource.get('link')
        resource_id = resource.get('id')
        default_category_id = resource.get('default_category')
        default_tag_id = resource.get('default_tag')
        gap = resource.get('refresh_gap')
        status = resource.get('refresh_status')
        last_refresh_time = parse_datetime(resource.get('last_refresh_time'))
        proxy = resource.get('proxy')
        auth = resource.get('auth')

        if auth:
            username = auth.get('username')
            password = auth.get('password')
            cookie = auth.get('cookie')
            auth_header = auth.get('auth_header')
            auth_value = auth.get('auth_value')
        else:
            username, password, cookie, auth_header, auth_value = (None,) * 5

        task_data = {
            'loop': loop,
            'init_url': link,
            'resource_id': resource_id,
            'default_category_id': default_category_id,
            'default_tag_id': default_tag_id,
            'proxy': proxy,
            'username': username,
            'password': password,
            'cookie': cookie,
            'auth_header': auth_header,
            'auth_value': auth_value
        }

        if status in (enums.ResourceRefreshStatus.NEVER.value, enums.ResourceRefreshStatus.FAIL.value):
            next_run_time = datetime.datetime.now(tz=pytz.UTC)
        elif status == enums.ResourceRefreshStatus.RUNNING.value:
            continue
        else:
            next_run_time = last_refresh_time + datetime.timedelta(hours=gap)

        task_id = f'{resource.get("name")}-({resource.get("spider_type").get("id")},{resource_id})'

        job = scheduler.get_job(job_id=task_id)
        if job:
            job.modify(
                next_run_time=max(next_run_time, datetime.datetime.now(tz=pytz.UTC))
            )
        else:
            scheduler.add_job(
                func=spider_class.get_spider(**task_data),
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
        trigger='cron',
        second='*/10',
        misfire_grace_time=600,
        max_instances=2,
        coalesce=True,
        id='refresh-task'
    )
    scheduler.start()

    asyncio.ensure_future(save.consume(loop, save.save_queue))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info(f'退出......')
        executor.shutdown(wait=False)
        scheduler.shutdown(wait=False)
        loop.close()

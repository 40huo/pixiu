import asyncio
import datetime
import importlib
import logging
import re

import pytz
from apscheduler.events import EVENT_JOB_MAX_INSTANCES, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from django.utils.dateparse import parse_datetime

from backend.pipelines import save
from utils import enums
from utils.http_req import api_report_spider_event, api_update_resource, api_fetch_resource_list

logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("django.request").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("chardet").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
spider_id_pattern = re.compile(r"\((\d+),(\d+)\)$")


def spider_listener(event):
    """
    apscheduler事件回调
    :param event:
    :return:
    """
    try:
        match = spider_id_pattern.search(event.job_id)
        if match:
            spider_id = int(match.group(1))
            resource_id = int(match.group(2))
            if event.code == EVENT_JOB_ERROR:
                msg = f"任务 {event.job_id} 出现异常 {event.traceback}"
                logger.error(msg)
                level = 4
            elif event.code == EVENT_JOB_MISSED:
                msg = f"任务 {event.job_id} 错过执行时间 {event.scheduled_run_time}"
                logger.warning(msg)
                level = 3
            elif event.code == EVENT_JOB_MAX_INSTANCES:
                msg = f"任务 {event.job_id} 达到最大同时执行数量"
                logger.warning(msg)
                level = 3
            else:
                msg = f"任务 {event.job_id} 出现未知异常"
                logger.warning(msg)
                level = 3

            asyncio.ensure_future(api_report_spider_event(level=level, message=msg, spider_id=spider_id))

            asyncio.ensure_future(
                api_update_resource(
                    refresh_status=enums.ResourceRefreshStatus.FAIL.value,
                    last_refresh_time=datetime.datetime.now(),
                    resource_id=resource_id,
                )
            )
        else:
            logger.error(f"任务id中不存在爬虫id {event}")
    except Exception as e:
        logger.exception(f"处理任务异常时出错 {e}")


async def refresh_task(loop, scheduler: AsyncIOScheduler):
    """
    任务获取
    :param loop: 协程loop
    :param scheduler: apscheduler
    :return:
    """
    result = await api_fetch_resource_list(loop=loop)
    for resource in result:
        is_enabled = resource.get("is_enabled")
        if not is_enabled:
            continue

        spider_class = importlib.import_module(
            f'.{resource.get("spider_type").get("filename")}', package="backend.spiders"
        )
        link = resource.get("link")
        resource_id = resource.get("id")
        default_category_id = resource.get("default_category")
        default_tag_id = resource.get("default_tag")
        gap = resource.get("refresh_gap")
        status = resource.get("refresh_status")
        last_refresh_time = parse_datetime(resource.get("last_refresh_time"))
        proxy = resource.get("proxy")
        auth = resource.get("auth")

        if auth:
            username = auth.get("username")
            password = auth.get("password")
            cookie = auth.get("cookie")
            auth_header = auth.get("auth_header")
            auth_value = auth.get("auth_value")
        else:
            username, password, cookie, auth_header, auth_value = (None,) * 5

        task_data = {
            "loop": loop,
            "init_url": link,
            "resource_id": resource_id,
            "default_category_id": default_category_id,
            "default_tag_id": default_tag_id,
            "proxy": proxy,
            "username": username,
            "password": password,
            "cookie": cookie,
            "auth_header": auth_header,
            "auth_value": auth_value,
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
            job.modify(next_run_time=max(next_run_time, datetime.datetime.now(tz=pytz.UTC)))
        else:
            scheduler.add_job(
                func=spider_class.get_spider(**task_data),
                trigger="date",
                next_run_time=max(next_run_time, datetime.datetime.now(tz=pytz.UTC)),
                id=task_id,
                name=resource.get("name"),
                misfire_grace_time=600,
                coalesce=True,
                replace_existing=True,
            )


async def init_task(loop):
    """
    初始化，将running状态重置
    :param loop: 协程loop
    :return:
    """
    result = await api_fetch_resource_list(loop=loop)
    for resource in result:
        status = resource.get("refresh_status")
        resource_id = resource.get("id")
        resource_name = resource.get("name")
        if status == enums.ResourceRefreshStatus.RUNNING.value:
            is_success = await api_update_resource(
                resource_id=resource_id, refresh_status=enums.ResourceRefreshStatus.FAIL.value
            )
            if is_success:
                logger.info(f"重置 {resource_name} 订阅源状态成功")
            else:
                logger.error(f"重置 {resource_name} 订阅源状态失败")


def run():
    """
    后端爬虫入口
    :return:
    """
    loop = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler()

    scheduler.add_listener(spider_listener, mask=EVENT_JOB_MAX_INSTANCES | EVENT_JOB_ERROR | EVENT_JOB_MISSED)

    asyncio.ensure_future(init_task(loop=loop), loop=loop)

    scheduler.add_job(
        func=refresh_task,
        args=(loop, scheduler),
        trigger="cron",
        second="*/10",
        misfire_grace_time=600,
        max_instances=2,
        coalesce=True,
        id="refresh-task",
    )
    scheduler.start()

    asyncio.ensure_future(save.consume(loop, save.save_queue), loop=loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info(f"退出......")
        scheduler.shutdown(wait=False)
        loop.close()

import asyncio
import concurrent.futures
import datetime
import logging
from urllib.parse import urljoin

from rest_framework.reverse import reverse
from rest_framework.test import RequestsClient

from pixiu.settings import TOKEN

client = RequestsClient()
base_url = "http://testserver/"
logger = logging.getLogger(__name__)
thread_executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)


def send_req(method: str, url: str, data: dict = None, headers: dict = None):
    """
    封装HTTP请求
    :param method: 请求方法
    :param url: 请求URL，相对路径
    :param data: POST数据，默认JSON格式
    :param headers: 请求头
    :return:
    """
    if headers is None:
        headers = {"Authorization": f"Token {TOKEN}"}
    else:
        headers = headers

    if url.startswith("http"):
        logger.error(f"需要使用相对URL")
        return None
    else:
        abs_url = urljoin(base=base_url, url=url)

    if not abs_url.endswith("/"):
        abs_url += "/"

    if method.lower() == "get":
        return client.get(url=abs_url, headers=headers)
    elif method.lower() == "post":
        return client.post(url=abs_url, json=data, headers=headers)
    elif method.lower() == "patch":
        return client.patch(url=abs_url, json=data, headers=headers)
    else:
        logger.error(f"不受支持的请求方法 {method}")
        return None


async def api_report_spider_event(
    spider_id: int, level: int, message: str, loop: asyncio.AbstractEventLoop = None
) -> bool:
    """
    上报爬虫异常事件
    :param spider_id:
    :param level:
    :param message:
    :param loop:
    :return:
    """
    if loop is None:
        loop = asyncio.get_event_loop()

    post_data = {"level": level, "message": message, "spider": spider_id}
    req = await loop.run_in_executor(
        thread_executor, send_req, "post", reverse(viewname="spider-event-list"), post_data
    )

    if req.status_code == 201:
        logger.info("任务异常事件上报成功")
        return True
    else:
        logger.warning(f"任务异常事件上报失败，状态码 {req.status_code}，响应详情 {req.text}")
        return False


async def api_update_resource(
    resource_id: int,
    refresh_status: int = None,
    last_refresh_time: datetime.datetime = None,
    loop: asyncio.AbstractEventLoop = None,
) -> bool:
    """
    更新订阅源状态
    :param resource_id:
    :param refresh_status:
    :param last_refresh_time:
    :param loop:
    :return:
    """
    if loop is None:
        loop = asyncio.get_event_loop()

    patch_data = {}

    if refresh_status and isinstance(refresh_status, int):
        patch_data["refresh_status"] = refresh_status

    if last_refresh_time:
        patch_data["last_refresh_time"] = datetime.datetime.strftime(last_refresh_time, "%Y-%m-%dT%H:%M:%S")

    req = await loop.run_in_executor(
        thread_executor, send_req, "patch", reverse(viewname="resource-detail", args=[resource_id]), patch_data,
    )

    if req.status_code == 200:
        logger.info("更新订阅源状态成功")
        return True
    else:
        logger.warning(f"更新订阅源状态失败，状态码 {req.status_code}，响应详情 {req.text}")
        return False


async def api_fetch_resource_list(loop: asyncio.AbstractEventLoop = None) -> dict:
    """
    请求订阅源列表
    :param loop:
    :return:
    """
    if loop is None:
        loop = asyncio.get_event_loop()

    req = await loop.run_in_executor(thread_executor, send_req, "get", reverse(viewname="resource-list"))
    if req.status_code == 200:
        logger.debug("请求/api/resource/成功")
        return req.json()
    else:
        msg = f"resource API请求失败 {req.json()}"
        logger.error(msg)
        raise Exception(msg)

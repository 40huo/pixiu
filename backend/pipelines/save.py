import asyncio
import datetime
import logging

from lxml.html.clean import Cleaner
from rest_framework.reverse import reverse

from utils.http_req import send_req, thread_executor

logger = logging.getLogger(__name__)
save_queue = asyncio.Queue(maxsize=1024)


class Post(object):
    """
    存储文章
    """

    def __init__(self, title: str, url: str, content: str, pub_time, source: int, category: int, tag: int, hash: str):
        self.title = title
        self.url = url
        self.content = content
        self.pub_time = pub_time
        self.source = source
        self.category = category
        self.tag = tag
        self.hash = hash


def change_referer_policy(tag_obj, tag_name: str, referrer_policy: "str" = "no-referrer"):
    """
    处理Referrer Policy
    :param tag_obj:
    :param tag_name: 标签名
    :param referrer_policy:
    :return:
    """
    tag_list = tag_obj.find_all(tag_name)
    for tag in tag_list:
        tag["referrerPolicy"] = referrer_policy

    return tag_obj


def html_clean(html_content):
    """
    清理HTML中的无用样式、脚本等
    :return:
    """
    cleaner = Cleaner(
        style=True, scripts=True, comments=True, javascript=True, page_structure=False, safe_attrs_only=True
    )
    return cleaner.clean_html(html=html_content)


async def produce(queue, data):
    """
    生产数据
    :param queue:
    :param data:
    :return:
    """
    await queue.put(data)
    logger.debug(f"写入存储队列 {data.title}")


async def consume(loop, queue):
    """
    消费队列数据
    :return:
    """
    while True:
        data = await queue.get()
        logger.debug(f"读取存储队列 {data.title}")

        post_data = data.__dict__
        post_data["pub_time"] = datetime.datetime.strftime(data.pub_time, "%Y-%m-%dT%H:%M:%S")

        req = await loop.run_in_executor(thread_executor, send_req, "post", reverse(viewname="article-list"), post_data)
        if req.status_code == 201:
            logger.info(f"存储成功 {data.title}")
        elif req.status_code == 400:
            logger.debug(f"重复文章 {data.title}")
        else:
            logger.error(f"存储失败，状态码 {req.status_code} 响应详情 {req.text}")

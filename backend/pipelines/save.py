import asyncio
import datetime
import json

from lxml.html.clean import Cleaner

from utils.log import Logger

save_queue = asyncio.Queue(maxsize=1024)
save_queue.get()
logger = Logger(__name__).get_logger()


def html_clean(html_content):
    """
    清理HTML中的无用样式、脚本等
    :return:
    """
    cleaner = Cleaner(
        style=True,
        scripts=True,
        comments=True,
        javascript=True,
        page_structure=False,
        safe_attrs_only=True
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
    logger.debug(f'写入存储队列 {data}')


async def consume(queue):
    """
    消费队列数据
    :return:
    """
    from rest_framework.test import RequestsClient

    client = RequestsClient()
    while True:
        data = await queue.get()
        logger.debug(f'读取存储队列 {data}')

        try:
            post_data = {
                'title': data.get('title'),
                'url': data.get('url'),
                'content': data.get('content'),
                'pub_time': datetime.datetime.strftime(data.get('publish_time'), '%Y-%m-%dT%H:%M:%S'),
                'source': data.get('resource_id'),
                'category': data.get('default_category_id'),
                'tag': data.get('default_tag_id')
            }

            resp = client.post(url='http://testserver/api/article/', json=post_data, headers={'Authorization': 'Token a75598cbe08be4a7823045101b55b39c762cac6a'})
            logger.debug(resp.text)

        except json.JSONDecodeError:
            logger.error(f'JSON解析失败 {data}')

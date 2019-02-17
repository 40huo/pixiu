import asyncio

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
    while True:
        data = await queue.get()
        logger.debug(f'读取存储队列 {data}')

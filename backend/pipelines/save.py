import asyncio

from lxml.html.clean import Cleaner

save_queue = asyncio.Queue(maxsize=1024)
save_queue.get()


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


async def consume(queue):
    """
    消费队列数据
    :return:
    """
    while True:
        data = await queue.get()

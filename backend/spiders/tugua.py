import asyncio
import datetime
import urllib.parse

import aiohttp
from bs4 import BeautifulSoup

from backend.pipelines import save
from backend.pipelines.save import html_clean
from backend.spiders.base import BaseSpider
from utils import enums
from utils.log import Logger

logger = Logger(__name__).get_logger()


def get_spider(*args, **kwargs):
    return TuguaSpider(*args, **kwargs).run


class TuguaSpider(BaseSpider):
    """
    喷嚏图卦
    """

    def __init__(self, loop, init_url: str, resource_id: int = None, default_category_id: int = None, default_tag_id: int = None, headers: str = None, *args, **kwargs):
        super().__init__(loop, init_url, resource_id, default_category_id, default_tag_id, headers, *args, **kwargs)

    async def parse_article(self, article_link: str, session) -> dict:
        """
        解析文章内容
        :param article_link: 文章链接
        :param session: aiohttp Session
        :return:
        """
        article_html = await self.get_html(article_link, session)
        if article_html:
            soup = BeautifulSoup(article_html, 'lxml')

            tugua_title = soup.select('td.oblog_t_4')[0].find_all('a')[1].get_text()
            tugua_content = str(soup.select('div.oblog_text')[0])
            publish_time = soup.select('span.oblog_text')[0].get_text()
            publish_time = datetime.datetime.strptime(publish_time.replace('xilei 发布于 ', ''), '%Y-%m-%d %H:%M:%S')
            clean_content = html_clean(tugua_content)

            return {
                'title': tugua_title,
                'url': article_link,
                'content': clean_content,
                'publish_time': publish_time,
                'resource_id': self.resource_id,
                'default_category_id': self.default_category_id,
                'default_tag_id': self.default_tag_id,
                'hash': self.gen_hash(clean_content.encode(errors='ignore'))
            }

    async def parse_link(self, init_url: str, session, max_count: int) -> list:
        """
        解析文章地址
        :param init_url: 入口地址
        :param session: aiohttp Session
        :param max_count: 解析数量
        :return:
        """
        init_html = await self.get_html(init_url, session)
        if init_html:
            soup = BeautifulSoup(init_html, 'lxml')
            node_list = soup.select('ul > li')
            relative_links = [node.find('a').get('href') for node in node_list[:max_count]]
            detail_links = [urllib.parse.urljoin(base=init_url, url=link) for link in relative_links]
            return detail_links

    async def run(self):
        await self.update_resource(status=enums.ResourceRefreshStatus.RUNNING.value)
        async with aiohttp.ClientSession() as session:
            article_links = await self.parse_link(self.init_url, session, max_count=10)
            tasks = [self.parse_article(link, session) for link in article_links]
            for coro in asyncio.as_completed(tasks):
                data = await coro
                await save.produce(save.save_queue, data=data)

            # 爬取结束，更新resource中的last_refresh_time
            await self.update_resource(status=enums.ResourceRefreshStatus.SUCCESS.value)

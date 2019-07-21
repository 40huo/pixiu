import asyncio
import datetime
import urllib.parse

import aiohttp
from bs4 import BeautifulSoup

from backend.pipelines.save import Post, html_clean, change_referer_policy
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

    def __init__(
            self,
            loop,
            init_url: str,
            resource_id: int = None,
            default_category_id: int = None,
            default_tag_id: int = None,
            headers: str = None,
            *args,
            **kwargs
    ):
        super().__init__(loop, init_url, resource_id, default_category_id, default_tag_id, headers, *args, **kwargs)

    async def parse_article(self, article_link: str, session):
        """
        解析文章内容
        :param article_link: 文章链接
        :param session: aiohttp Session
        :return:
        """
        article_html = await self.fetch_html(article_link, session)
        if article_html:
            soup = BeautifulSoup(article_html, 'lxml')

            tugua_title = soup.find('td', class_='oblog_t_4').find_all('a')[1].get_text()
            origin_content = str(soup.find('div', class_='oblog_text'))
            no_referer_content = str(change_referer_policy(soup.find('div', class_='oblog_text'), tag_name='img'))
            publish_time = soup.select('span.oblog_text')[0].get_text()
            publish_time = datetime.datetime.strptime(publish_time.replace('xilei 发布于 ', ''), '%Y-%m-%d %H:%M:%S')
            clean_content = html_clean(origin_content)

            new_post = Post(
                title=tugua_title,
                url=article_link,
                content=no_referer_content,
                pub_time=publish_time,
                source=self.resource_id,
                category=self.default_category_id,
                tag=self.default_tag_id,
                hash=self.gen_hash(clean_content)
            )

            await self.save(new_post)

    async def parse_link(self, init_url: str, session, max_count: int) -> list:
        """
        解析文章地址
        :param init_url: 入口地址
        :param session: aiohttp Session
        :param max_count: 解析数量
        :return:
        """
        init_html = await self.fetch_html(init_url, session)
        if init_html:
            soup = BeautifulSoup(init_html, 'html5lib')
            title_list = soup.find_all('div', class_='title')
            detail_links = []
            for title in title_list:
                if title.find('a', text='喷嚏图卦'):
                    node_list = title.find_next('div', class_='title_down').find('ul').find_all('li')
                    relative_links = [node.find('a').get('href') for node in node_list[:max_count]]
                    detail_links = [urllib.parse.urljoin(base=init_url, url=link) for link in relative_links]

            return detail_links

    async def run(self):
        await self.update_resource(status=enums.ResourceRefreshStatus.RUNNING.value)
        async with aiohttp.ClientSession() as session:
            article_links = await self.parse_link(self.init_url, session, max_count=10)
            tasks = [self.parse_article(link, session) for link in article_links]
            await asyncio.gather(*tasks)

            # 爬取结束，更新resource中的last_refresh_time
            await self.update_resource(status=enums.ResourceRefreshStatus.SUCCESS.value)

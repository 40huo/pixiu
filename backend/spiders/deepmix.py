import datetime
import re

import requests
from bs4 import BeautifulSoup

from backend.pipelines import save
from backend.spiders.base import BaseSpider
from utils import enums
from utils.log import Logger
from ..scheduler import executor

logger = Logger(__name__).get_logger()


def get_spider(*args, **kwargs):
    return DeepMixSpider(*args, **kwargs).run


class DeepMixSpider(BaseSpider):
    """
    暗网中文论坛
    """
    session = requests.session()
    deepmix_index_url = ''
    REFRESH_LIMIT = 30

    def __init__(self, loop, init_url: str, resource_id: int = None, default_category_id: int = None, default_tag_id: int = None, headers: str = None, *args, **kwargs):
        super().__init__(loop, init_url, resource_id, default_category_id, default_tag_id, headers, *args, **kwargs)

        proxy = kwargs.pop('proxy', None)
        if proxy is None:
            self.proxy = {
                'http': 'socks5h://127.0.0.1:9150',
                'https': 'socks5h://127.0.0.1:9150'
            }
        else:
            self.proxy = {
                'http': proxy,
                'https': proxy
            }

        username = kwargs.pop('username', '')
        password = kwargs.pop('password', '')
        self.username = username
        self.password = password
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0'
        self.session.proxies = self.proxy
        self.session.headers = self.headers

        self.refresh_time = 0

    def refresh_session(self, raw_html: str) -> bool:
        """
        刷新session
        :return:
        """
        if self.refresh_time > self.REFRESH_LIMIT:
            logger.warning(f'达到刷新次数上线 {self.REFRESH_LIMIT}')
            return False
        else:
            self.refresh_time += 1

        # 第一次
        logger.debug(f'第一次请求 获取真正入口 {self.init_url}')
        match = re.search(r'url=(http://deepmix\w+\.onion)\">', raw_html)
        if self.username in raw_html:
            return True
        if not match:
            logger.error(f'初始地址失效，返回内容 {raw_html}')
            return False
        index_url = match.group(1)

        # 第二次
        self.deepmix_index_url = index_url
        logger.debug(f'第二次请求 获取首页 {index_url}')
        index_req = self.session.get(index_url)
        match = re.search(r'url=(/\S+)\">', index_req.text)
        if self.username in index_req.text:
            return True
        if not match:
            logger.error(f'首页请求失败，返回内容 {index_req.text}')
            return False
        pre_login_url = f'{index_url}{match.group(1)}'
        match = re.search(r'autim=(\d+)', pre_login_url)
        if not match:
            logger.error(f'autim参数获取失败，返回内容 {pre_login_url}')
            return False
        autim = match.group(1)

        # 第三次
        logger.debug(f'第三次请求 跳转登录页 {pre_login_url}')
        pre_login_req = self.session.get(pre_login_url)
        match = re.search(r'name=\"sid\" value=\"(\w+)\"', pre_login_req.text)
        if self.username in pre_login_req.text:
            return True
        if not match:
            logger.error(f'sid参数获取失败，返回内容 {pre_login_req.text}')
            return False
        sid = match.group(1)

        # 第四次
        post_data = {
            'sid': sid,
            'redirect': 'index.php',
            'login': '登录',
            'autim': autim,
            'username': self.username,
            'password': self.password
        }
        login_url = f'{index_url}/ucp.php?mode=login'
        logger.debug(f'第四次请求 登录POST {login_url}')
        login_req = self.session.post(login_url, data=post_data)
        if self.username in login_req.text:
            return True
        else:
            logger.error(f'首页内容检测失败')
            return False

    async def parse_topic(self, topic_url) -> tuple:
        """
        解析帖子内容
        :param topic_url: 
        :return: 
        """
        try:
            req = await self.loop.run_in_executor(executor, self.session.get, topic_url)
            if self.username not in req.text:
                logger.warning(f'页面内容异常，可能返回了节点选择页面')
                is_session_success = await self.loop.run_in_executor(executor, self.refresh_session, req.text)
                if is_session_success:
                    return await self.parse_topic(topic_url)
                else:
                    return None, None

            soup = BeautifulSoup(req.text, 'lxml')
            pub_time = datetime.datetime.strptime(soup.find('p', class_='author').contents[-1].strip(), "%Y年-%m月-%d日 %H:%M")
            content = save.html_clean(str(soup.find('div', class_='content')))

            return pub_time, content
        except Exception as e:
            logger.error(f'获取帖子 {topic_url} 详情异常 {e}', exc_info=True)
            return None, None

    async def parse_list(self, path) -> list:
        """
        解析帖子列表
        :param path:
        :return:
        """
        result_list = list()
        list_url = f'{self.deepmix_index_url}/{path}'
        req = await self.loop.run_in_executor(executor, self.session.get, list_url)
        if self.username not in req.text:
            logger.warning(f'页面内容异常，可能返回了节点选择页面')
            is_session_success = await self.loop.run_in_executor(executor, self.refresh_session, req.text)
            if is_session_success:
                return await self.parse_list(path)
            else:
                return []

        soup = BeautifulSoup(req.text, 'lxml')
        data_table = soup.select('.m_area_a > tr')
        for i in data_table:
            if i.find_next('td').get_text().isdigit():
                a_tag = i.find('div', {'class': 'length_400'}).find_next('a')
                topic_url = f"{self.deepmix_index_url}{a_tag.get('href')}"
                title = a_tag.get_text()

                pub_time, content = await self.parse_topic(topic_url=topic_url)

                if pub_time and content:
                    result_list.append({
                        'title': title,
                        'url': topic_url,
                        'content': content,
                        'publish_time': pub_time,
                        'resource_id': self.resource_id,
                        'default_category_id': self.default_category_id,
                        'default_tag_id': self.default_tag_id,
                        'hash': self.gen_hash(a_tag.get('href').encode(errors='ignore'))
                    })

        return result_list

    async def run(self):
        await self.update_resource(status=enums.ResourceRefreshStatus.RUNNING.value)
        init_req = await self.loop.run_in_executor(executor, self.session.get, self.init_url)
        is_session_success = await self.loop.run_in_executor(executor, self.refresh_session, init_req.text)
        if is_session_success:
            for zone in ('pay/user_area.php?q_ea_id=10001',):
                data_list = await self.parse_list(zone)
                if len(data_list):
                    logger.info(f'抓取到 {len(data_list)} 条暗网数据')
                    for data in data_list:
                        await save.produce(save.save_queue, data=data)

                    # 爬取结束，更新resource中的last_refresh_time
                    await self.update_resource(status=enums.ResourceRefreshStatus.SUCCESS.value)
                else:
                    logger.error(f'抓取帖子异常')
                    await self.update_resource(status=enums.ResourceRefreshStatus.FAIL.value)
        else:
            logger.error('登陆失败，退出')
            await self.update_resource(status=enums.ResourceRefreshStatus.FAIL.value)

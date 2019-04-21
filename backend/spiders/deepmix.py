import concurrent.futures
import datetime
import re

import requests
from bs4 import BeautifulSoup

from backend.pipelines import save
from backend.spiders.base import BaseSpider
from utils.log import Logger

logger = Logger(__name__).get_logger()


def get_spider(*args, **kwargs):
    return DeepMixSpider(*args, **kwargs).run


class DeepMixSpider(BaseSpider):
    """
    暗网中文论坛
    """
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    session = requests.session()
    deepmix_index_url = ''

    def __init__(self, loop, init_url: str, resource_id: int = None, default_category_id: int = None, default_tag_id: int = None, headers: str = None, *args, **kwargs):
        super().__init__(loop, init_url, headers, resource_id, default_category_id, default_tag_id, *args, **kwargs)

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

    def login(self) -> bool:
        """
        登录
        :return:
        """
        logger.debug(f'第一次请求 获取真正入口 {self.init_url}')
        init_req = self.session.get(self.init_url)
        match = re.search(r'url=(http://deepmix\w+\.onion)\">', init_req.text)
        if not match:
            logger.error(f'初始地址失效')
            return False

        index_url = match.group(1)
        self.deepmix_index_url = index_url
        logger.debug(f'第二次请求 获取首页 {index_url}')
        index_req = self.session.get(index_url)
        match = re.search(r'url=(/\S+)\">', index_req.text)
        if not match:
            logger.error(f'首页请求失败')
            return False

        pre_login_url = f'{index_url}{match.group(1)}'
        logger.debug(f'第三次请求 跳转登录页 {pre_login_url}')
        pre_login_req = self.session.get(pre_login_url)

        login_url = f'{index_url}/ucp.php?mode=login'
        logger.debug(f'第四次请求 登录POST {login_url}')

        match = re.search(r'autim=(\d+)', pre_login_url)
        if not match:
            logger.error(f'autim参数获取失败')
            return False
        autim = match.group(1)

        match = re.search(r'name=\"sid\" value=\"(\w+)\"', pre_login_req.text)
        if not match:
            logger.error(f'sid参数获取失败')
            return False
        sid = match.group(1)

        post_data = {
            'sid': sid,
            'redirect': 'index.php',
            'login': '登录',
            'autim': autim,
            'username': self.username,
            'password': self.password
        }
        login_req = self.session.post(login_url, data=post_data)
        if '暗网欢迎您' in login_req.text:
            return True
        else:
            logger.error(f'首页内容检测失败')
            return False

    def parse(self, path) -> list:
        result_list = list()
        url = f'{self.deepmix_index_url}/{path}'
        req = self.session.get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        data_table = soup.select('.m_area_a > tbody:nth-of-type(1) > tr')
        for i in data_table:
            if i.find_next('td').get_text().isdigit():
                pub_time = datetime.datetime.strptime(i.find_all('td')[1].get_text(), '%m-%d %H:%M').replace(year=datetime.datetime.today().year)
                a_tag = i.find('div', {'class': 'length_400'}).find_next('a')
                url = f"{self.deepmix_index_url}{a_tag.get('href')}"
                title = a_tag.get_text()

                result_list.append({
                    'title': title,
                    'url': url,
                    'content': f"根据法律法规，详细内容不采集，请自行访问 {a_tag.get('href')} 查看。",
                    'publish_time': pub_time,
                    'resource_id': self.resource_id,
                    'default_category_id': self.default_category_id,
                    'default_tag_id': self.default_tag_id,
                    'hash': self.gen_hash(a_tag.get('href').encode(errors='ignore'))
                })

        return result_list

    async def save(self, data: dict):
        """
        存储
        :return:
        """
        await save.produce(save.save_queue, data=data)

    async def run(self):
        is_login = await self.loop.run_in_executor(self.executor, self.login)
        if is_login:
            for zone in ('pay/user_area.php?q_ea_id=10001',):
                data_list = await self.loop.run_in_executor(self.executor, self.parse, zone)
                for data in data_list:
                    await self.save(data=data)
        else:
            logger.error('登陆失败，退出')
            return None

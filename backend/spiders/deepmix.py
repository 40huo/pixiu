import datetime
import re

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

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

        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))

        self.refresh_time = 0

    def _fetch_html(self, url, method: str = 'get', post_data: dict = None):
        if method == 'get':
            req = self.session.get(url)
        elif method == 'post':
            req = self.session.post(url=url, data=post_data)
        else:
            logger.warning(f'不支持的请求方法 {method}')
            return None

        return self._verify_session(raw_html=req.text)

    def _verify_session(self, raw_html: str) -> bool:
        """
        刷新session
        :return:
        """
        init_re = re.compile(r'缓存已经过期或点击太快')
        index_re = re.compile(r'url=(http://deepmix\w+\.onion)\">')
        pre_login_re = re.compile(r'url=(/\S+)\">')
        autim_re = re.compile(r'id=\"autim\" value=\"(\d+)\"')
        sid_re = re.compile(r'name=\"sid\" value=\"(\w+)\"')

        if self.refresh_time > self.REFRESH_LIMIT:
            logger.warning(f'达到刷新次数上线 {self.REFRESH_LIMIT}')
            return False
        else:
            self.refresh_time += 1

        if self.username in raw_html:
            logger.info('Session验证成功')
            self.refresh_time = 0
            return True
        elif init_re.search(raw_html) or raw_html == '':
            # 第一次
            logger.info(f'请求初始页面 {self.init_url}')
            return self._fetch_html(url=self.init_url, method='get')
        elif index_re.search(raw_html):
            # 获取到首页入口
            index_url = index_re.search(raw_html).group(1)
            self.deepmix_index_url = index_url
            logger.info(f'请求首页 {index_url}')
            return self._fetch_html(url=index_url, method='get')
        elif pre_login_re.search(raw_html):
            pre_login_url = f'{self.deepmix_index_url}{pre_login_re.search(raw_html).group(1)}'
            logger.info(f'请求登录跳转页 {pre_login_url}')
            return self._fetch_html(url=pre_login_url, method='get')
        elif sid_re.search(raw_html):
            sid = sid_re.search(raw_html).group(1)
            autim = autim_re.search(raw_html).group(1)
            post_data = {
                'sid': sid,
                'redirect': 'index.php',
                'login': '登录',
                'autim': autim,
                'username': self.username,
                'password': self.password
            }
            login_url = f'{self.deepmix_index_url}/ucp.php?mode=login'
            logger.info(f'发送登录请求 {login_url}')
            return self._fetch_html(url=login_url, method='post', post_data=post_data)
        else:
            logger.error(f'Session验证失败，未知HTML内容 {raw_html}')

    def parse_topic(self, topic_url) -> tuple:
        """
        解析帖子内容
        :param topic_url: 
        :return: 
        """
        try:
            req = self.session.get(topic_url)
            if self.username not in req.text:
                logger.warning(f'页面内容异常，可能返回了节点选择页面')
                is_session_success = self._verify_session(req.text)
                if is_session_success:
                    return self.parse_topic(topic_url)
                else:
                    return None, None

            soup = BeautifulSoup(req.text, 'lxml')
            pub_time = datetime.datetime.strptime(soup.find('p', class_='author').contents[-1].strip(), "%Y年-%m月-%d日 %H:%M")
            content = save.html_clean(str(soup.find('div', class_='content')))

            return pub_time, content
        except Exception as e:
            logger.error(f'获取帖子 {topic_url} 详情异常 {e}', exc_info=True)
            return None, None

    def parse_list(self, path) -> list:
        """
        解析帖子列表
        单线程减少session失效的情况
        :param path:
        :return:
        """
        result_list = list()
        list_url = f'{self.deepmix_index_url}/{path}'
        req = self.session.get(list_url)
        if self.username not in req.text:
            logger.warning(f'页面内容异常，可能返回了节点选择页面')
            is_session_success = self._verify_session(req.text)
            if is_session_success:
                return self.parse_list(path)
            else:
                return []

        soup = BeautifulSoup(req.text, 'lxml')
        data_table = soup.select('.m_area_a > tr')
        for i in data_table:
            if i.find_next('td').get_text().isdigit():
                a_tag = i.find('div', class_='length_400').find_next('a')
                topic_url = f"{self.deepmix_index_url}{a_tag.get('href')}"
                title = a_tag.get_text()

                pub_time, content = self.parse_topic(topic_url=topic_url)
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
        is_session_success = await self.loop.run_in_executor(executor, self._verify_session, '')
        if is_session_success:
            for zone in ('pay/user_area.php?q_ea_id=10001',):
                data_list = await self.loop.run_in_executor(executor, self.parse_list, zone)
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

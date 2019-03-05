import asyncio
import datetime
import hashlib

from rest_framework.test import RequestsClient

from pixiu.settings import TOKEN
from utils.log import Logger


class BaseSpider(object):
    def __init__(self, init_url: str, headers: str = None, resource_id: int = None, default_category_id: int = None, default_tag_id: int = None):
        self.init_url = init_url
        self.resource_id = resource_id
        self.default_category_id = default_category_id
        self.default_tag_id = default_tag_id

        self.headers = headers if headers else {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
        }

        self.logger = Logger(__name__).get_logger()

    @asyncio.coroutine
    async def get_html(self, url: str, session, method: str = 'GET', post_data: str = None, encoding: str = None):
        """
        获取HTML内容
        :param url: 链接
        :param session: aiohttp Session对象
        :param method: 请求方法
        :param post_data: POST 数据
        :param encoding: 编码
        :return: 请求返回内容
        """
        try:
            if method == 'GET':
                async with session.get(url=url, headers=self.headers) as resp:
                    return await resp.text(encoding=encoding, errors='ignore')
            elif method == 'POST' and post_data is not None:
                async with session.post(url=url, headers=self.headers, data=post_data) as resp:
                    return await resp.text(encoding=encoding, errors='ignore')
            else:
                self.logger.warning(f'Unsupported HTTP method: {method}')
                return None
        except UnicodeDecodeError:
            self.logger.error(f'Decode error: {url}')
            return None
        except Exception as e:
            self.logger.error(f'未知错误 {e}', exc_info=1)
            return None

    def save(self, data: dict):
        """
        存储数据库
        :param data: 需要存入队列的数据
        :return:
        """
        raise NotImplementedError('Spider must customize save method!')

    @staticmethod
    def gen_hash(content: bytes) -> str:
        """
        计算Hash值
        :param content:
        :return:
        """
        return hashlib.sha1(content).hexdigest()

    def update_resource(self):
        client = RequestsClient()
        resp = client.patch(
            url=f'http://testserver/api/resource/{self.resource_id}/',
            json={'last_refresh_time': datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%S')},
            headers={'Authorization': f'Token {TOKEN}'}
        )
        if resp.status_code == 200:
            self.logger.info(f'更新 {self.resource_id} 订阅源last_refresh_time成功')
        else:
            self.logger.error(f'更新 {self.resource_id} 订阅源last_refresh_time失败，状态码 {resp.status_code}，响应 {resp.text}')

    async def run(self):
        """
        爬虫入口
        :return:
        """
        raise NotImplementedError('Spider must override this method!')

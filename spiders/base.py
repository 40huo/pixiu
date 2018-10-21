import asyncio

from utils.log import Logger


class BaseSpider(object):
    def __init__(self, init_url, headers=None):
        self.init_url = init_url
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
        :return: 请求返回内容
        """
        try:
            if method == 'GET':
                async with session.get(url=url, headers=self.headers) as resp:
                    assert resp.status == 200
                    return await resp.text(encoding=encoding, errors='ignore')
            elif method == 'POST' and post_data is not None:
                async with session.post(url=url, headers=self.headers, data=post_data) as resp:
                    assert resp.status == 200
                    return await resp.text(encoding=encoding, errors='ignore')
            else:
                self.logger.warning(f'Unsupported HTTP method: {method}')
                return None
        except AssertionError:
            self.logger.error(f'Unsupported status code {resp.status} while fetching {url}')
            return None
        except UnicodeDecodeError:
            self.logger.error(f'Decode error: {url}')

    def save(self):
        """
        存储数据库
        :return:
        """
        raise NotImplementedError('Spider must customize save method!')

    async def run(self):
        """
        爬虫入口
        :return:
        """
        raise NotImplementedError('Spider must override this method!')

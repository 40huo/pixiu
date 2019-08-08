from urllib.parse import urljoin

from loguru import logger
from rest_framework.test import RequestsClient

from pixiu.settings import TOKEN

client = RequestsClient()
base_url = "http://testserver/"


def send_req(method: str, url: str, data: dict = None, headers: dict = None):
    """
    封装HTTP请求
    :param method: 请求方法
    :param url: 请求URL，相对路径
    :param data: POST数据，默认JSON格式
    :param headers: 请求头
    :return:
    """
    if headers is None:
        headers = {"Authorization": f"Token {TOKEN}"}
    else:
        headers = headers

    if url.startswith("http"):
        logger.error(f"需要使用相对URL")
        return None
    else:
        abs_url = urljoin(base=base_url, url=url)

    if not abs_url.endswith("/"):
        abs_url += "/"

    if method.lower() == "get":
        return client.get(url=abs_url, headers=headers)
    elif method.lower() == "post":
        return client.post(url=abs_url, json=data, headers=headers)
    elif method.lower() == "patch":
        return client.patch(url=abs_url, json=data, headers=headers)
    else:
        logger.error(f"不受支持的请求方法 {method}")
        return None

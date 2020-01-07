import datetime
import hashlib
import logging

from aiohttp import ClientConnectorError
from rest_framework.reverse import reverse

from backend.pipelines import save
from backend.scheduler import executor
from utils import enums
from utils.http_req import send_req

logger = logging.getLogger(__name__)


class BaseSpider(object):
    def __init__(
        self,
        loop,
        init_url: str,
        resource_id: int = None,
        default_category_id: int = None,
        default_tag_id: int = None,
        headers: str = None,
        *args,
        **kwargs,
    ):
        self.loop = loop
        self.init_url = init_url
        self.resource_id = resource_id
        self.default_category_id = default_category_id
        self.default_tag_id = default_tag_id

        self.headers = headers or {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"
            )
        }

    async def fetch_html(self, url: str, session, method: str = "GET", post_data: str = None, encoding: str = None):
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
            if method.upper() == "GET":
                async with session.get(url=url, headers=self.headers) as resp:
                    return await resp.text(encoding=encoding, errors="ignore")
            elif method.upper() == "POST" and post_data is not None:
                async with session.post(url=url, headers=self.headers, data=post_data) as resp:
                    return await resp.text(encoding=encoding, errors="ignore")
            else:
                logger.warning(f"Unsupported HTTP method: {method}")
                return None
        except UnicodeDecodeError:
            logger.error(f"Decode error: {url}")
            return None
        except ClientConnectorError:
            logger.error(f"连接失败 {url}")
            return None
        except Exception as e:
            logger.exception(f"未知错误 {e}")
            return None

    @staticmethod
    def gen_hash(content: str) -> str:
        """
        计算Hash值
        :param content:
        :return:
        """
        return hashlib.sha1(content.encode(encoding="utf-8", errors="ignore")).hexdigest()

    @staticmethod
    async def save(data):
        """
        推到存储队列中
        :param data:
        :return:
        """
        await save.produce(save.save_queue, data=data)

    async def update_resource(self, status: int = enums.ResourceRefreshStatus.SUCCESS.value):
        patch_data = {"refresh_status": status}

        # 正在刷新时不更新刷新时间
        if status != enums.ResourceRefreshStatus.RUNNING.value:
            patch_data["last_refresh_time"] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%S")

        req = await self.loop.run_in_executor(
            executor, send_req, "patch", reverse(viewname="resource-detail", args=[self.resource_id]), patch_data
        )
        if req.status_code == 200:
            logger.info(f"更新 id={self.resource_id} 订阅源刷新时间与状态成功")
        else:
            logger.error(f"更新 id={self.resource_id} 订阅源刷新时间与状态失败，状态码 {req.status_code}，响应 {req.text}")

    async def run(self):
        """
        爬虫入口
        :return:
        """
        raise NotImplementedError("Spider must override this method!")

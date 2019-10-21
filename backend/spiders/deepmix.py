import asyncio
import datetime
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests.adapters import HTTPAdapter

from backend.pipelines import save
from backend.spiders.base import BaseSpider
from utils import enums
from ..scheduler import executor


def get_spider(*args, **kwargs):
    return DeepMixSpider(*args, **kwargs).run


class DeepMixSpider(BaseSpider):
    """
    暗网中文论坛
    """

    session = requests.session()
    deepmix_index_url = ""
    REFRESH_LIMIT = 30

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
        super().__init__(loop, init_url, resource_id, default_category_id, default_tag_id, headers, *args, **kwargs)

        proxy = kwargs.pop("proxy", None)
        if proxy is None:
            self.proxy = {"http": "socks5h://127.0.0.1:9150", "https": "socks5h://127.0.0.1:9150"}
        else:
            self.proxy = {"http": proxy, "https": proxy}

        username = kwargs.pop("username", "")
        password = kwargs.pop("password", "")
        self.username = username
        self.password = password

        tor_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0",
        }
        self.headers.update(tor_headers)
        self.session.proxies = self.proxy
        self.session.headers = self.headers

        self.session.mount("http://", HTTPAdapter(max_retries=3))
        self.session.mount("https://", HTTPAdapter(max_retries=3))

        self.__refresh_time = 0

    def __insecure_cookies(self):
        """
        secure的cookie不会跟随http请求发送，导致登录失败
        :return:
        """
        for c in self.session.cookies:
            c.secure = False

    def __fetch_html(self, url, method: str = "GET", post_data: dict = None):
        self.__insecure_cookies()
        if method.upper() == "GET":
            req = self.session.get(url)
        elif method.upper() == "POST":
            req = self.session.post(url=url, data=post_data)
        else:
            logger.warning(f"不支持的请求方法 {method}")
            return None

        return self.__verify_session(raw_html=req.text)

    def __verify_session(self, raw_html: str) -> bool:
        """
        刷新session
        :return:
        """
        title_pattern = re.compile(r"<title>(.*?)</title>")
        cache_expired_pattern = re.compile(r"缓存已经过期或点击太快")
        index_pattern = re.compile(r"url=(http://deepmix\w+\.onion)\">")
        pre_login_pattern = re.compile(r"<meta http-equiv=\"refresh\"\s+.+content=\".*;ucp\.php\?mode=login\">")
        sid_pattern = re.compile(r"name=\"sid\" value=\"(\w+)\"")
        form_token_pattern = re.compile(r"name=\"form_token\" value=\"(\w+)\"")
        creation_time_pattern = re.compile(r"name=\"creation_time\" value=\"(\w+)\"")

        if self.__refresh_time > self.REFRESH_LIMIT:
            logger.warning(f"达到刷新次数上线 {self.REFRESH_LIMIT}")
            return False
        else:
            self.__refresh_time += 1

        match = title_pattern.search(raw_html)
        if match:
            logger.info(f"页面title 【{match.group(1)}】")

        if not raw_html:
            # 第一次
            logger.info(f"请求初始页面 {self.init_url}")
            return self.__fetch_html(url=self.init_url, method="get")

        elif self.username in raw_html and "暗网欢迎您" in raw_html:
            logger.info("Session验证成功")
            return True

        elif cache_expired_pattern.search(raw_html):
            # 缓存过期
            logger.info(f"缓存过期，再次请求首页 {self.deepmix_index_url}")
            return self.__fetch_html(url=self.deepmix_index_url, method="get")

        elif index_pattern.search(raw_html):
            # 获取到首页入口
            index_url = index_pattern.search(raw_html).group(1)
            self.deepmix_index_url = index_url
            logger.info(f"请求首页 {index_url}")
            return self.__fetch_html(url=index_url, method="get")

        elif pre_login_pattern.search(raw_html):
            pre_login_url = urljoin(self.deepmix_index_url, "ucp.php?mode=login")
            logger.info(f"请求登录跳转页 {pre_login_url}")
            return self.__fetch_html(url=pre_login_url, method="get")

        elif (
            not sid_pattern.search(raw_html)
            and creation_time_pattern.search(raw_html)
            and form_token_pattern.search(raw_html)
        ):
            # 无效的登录页面
            real_login_url = urljoin(self.deepmix_index_url, "/ucp.php?mode=login")
            logger.debug(f"出现无效的的登录页面，重新请求 {real_login_url}")
            return self.__fetch_html(url=real_login_url, method="get")

        elif (
            sid_pattern.search(raw_html)
            and creation_time_pattern.search(raw_html)
            and form_token_pattern.search(raw_html)
        ):
            sid = sid_pattern.search(raw_html).group(1)
            creation_time = creation_time_pattern.search(raw_html).group(1)
            form_token = form_token_pattern.search(raw_html).group(1)
            post_data = {
                "creation_time": creation_time,
                "form_token": form_token,
                "sid": sid,
                "redirect": f"./ucp.php?mode=login&sid={sid}",
                "login": "登录",
                "username": self.username,
                "password": self.password,
            }
            login_url = f"{self.deepmix_index_url}/ucp.php?mode=login&sid={sid}"
            logger.info(f"发送登录请求 {login_url}")
            return self.__fetch_html(url=login_url, method="post", post_data=post_data)

        elif "提交的表单无效" in raw_html:
            logger.error(f"登录请求无效，需要更新爬虫 {raw_html}")
            return False

        else:
            logger.error(f"Session验证失败，未知HTML内容 {raw_html}")
            return False

    def parse_topic(self, topic_url) -> tuple:
        """
        解析帖子内容
        :param topic_url: 
        :return: 
        """
        try:
            req = self.session.get(topic_url)
            req.encoding = None
            soup = BeautifulSoup(req.text, "lxml")

            if self.username not in req.text:
                title = soup.find("title").get_text()
                logger.warning(f"页面内容异常，标题【{title}】")
                is_session_success = self.__verify_session(req.text)
                if is_session_success:
                    return self.parse_topic(topic_url)
                else:
                    return None, None

            pub_time = datetime.datetime.strptime(
                soup.find("p", class_="author").contents[-1].strip(), "%Y年-%m月-%d日 %H:%M"
            )
            content = save.html_clean(str(soup.find("div", class_="content")))

            self.__refresh_time = 0
            return pub_time, content
        except Exception as e:
            logger.opt(exception=True).error(f"获取帖子 {topic_url} 详情异常 {e}")
            return None, None

    def parse_list(self, path) -> list:
        """
        解析帖子列表
        单线程减少session失效的情况
        :param path:
        :return:
        """
        result_list = list()
        list_url = f"{self.deepmix_index_url}/{path}"
        req = self.session.get(list_url)
        if self.username not in req.text:
            logger.warning(f"页面内容异常，可能返回了节点选择页面")
            is_session_success = self.__verify_session(req.text)
            if is_session_success:
                return self.parse_list(path)
            else:
                return []

        soup = BeautifulSoup(req.text, "lxml")
        data_table = soup.select(".m_area_a > tr")
        for i in data_table:
            if i.find_next("td").get_text().isdigit():
                a_tag = i.find("div", class_="length_400").find_next("a")
                topic_url = f"{self.deepmix_index_url}{a_tag.get('href')}"
                title = a_tag.get_text()

                pub_time, content = self.parse_topic(topic_url=topic_url)
                if pub_time and content:
                    new_post = save.Post(
                        title=title,
                        url=topic_url,
                        content=content,
                        pub_time=pub_time,
                        source=self.resource_id,
                        category=self.default_category_id,
                        tag=self.default_tag_id,
                        hash=self.gen_hash(a_tag.get("href")),
                    )
                    result_list.append(new_post)
                    asyncio.ensure_future(self.save(data=new_post), loop=self.loop)

        return result_list

    async def run(self):
        await self.update_resource(status=enums.ResourceRefreshStatus.RUNNING.value)
        is_session_success = await self.loop.run_in_executor(executor, self.__verify_session, "")
        if is_session_success:
            for zone in ("pay/user_area.php?q_ea_id=10001",):
                data_list = await self.loop.run_in_executor(executor, self.parse_list, zone)
                if len(data_list):
                    logger.info(f"运行结束，抓取到 {len(data_list)} 条暗网数据")

                    # 爬取结束，更新resource中的last_refresh_time
                    await self.update_resource(status=enums.ResourceRefreshStatus.SUCCESS.value)
                else:
                    logger.error(f"抓取帖子异常")
                    await self.update_resource(status=enums.ResourceRefreshStatus.FAIL.value)
        else:
            logger.error("登陆失败，退出")
            await self.update_resource(status=enums.ResourceRefreshStatus.FAIL.value)

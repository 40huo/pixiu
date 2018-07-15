# -*- coding: utf-8 -*-
import datetime
from urllib import parse

import scrapy


class TuguaSpider(scrapy.Spider):
    name = 'tugua'
    allowed_domains = ['www.dapenti.com']
    start_urls = ['http://www.dapenti.com/blog/blog.asp?subjectid=70&name=xilei']
    headers = {
        'HOST': 'www.dapenti.com',
        'Referer': 'http://www.dapenti.com/blog/blog.asp?subjectid=70&name=xilei',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0',
    }

    def parse(self, response):
        """
        获取喷嚏图卦列表页所有文章链接
        :param response:
        :return:
        """
        tugua_post_nodes = response.xpath('/html/body/table/tbody/tr/td[1]/div/div[1]/ul/li')
        for tugua_post_node in tugua_post_nodes:
            tugua_post_url = tugua_post_node.xpath('./a/@href').extract_first('')
            yield scrapy.http.Request(
                url=parse.urljoin(response.url, tugua_post_url),
                headers=self.headers,
                callback=self.parse_detail,
            )
            break

    def parse_detail(self, response):
        """
        获取喷嚏图卦文章内容
        :param response:
        :return:
        """
        tugua_title = response.xpath('/html/body/table/tbody/tr/td[1]/div/table/tbody/tr[1]/td/div/span/span/a[2]/text()').extract_first('')
        tugua_content = response.xpath('/html/body/table/tbody/tr/td[1]/div/table/tbody/tr[2]/td/div[1]').extract_first('')
        publish_time = response.xpath('/html/body/table/tbody/tr/td[1]/div/table/tbody/tr[2]/td/table[1]/tbody/tr/td/div/span/text()').extract_first(datetime.datetime.now())
        publish_time = datetime.datetime.strptime(publish_time.replace('xilei 发布于 ', ''), '%Y-%m-%d %H:%M:%S')
        print(publish_time)

from backend import MAIN_LOOP
from backend.spiders.tugua import TuguaSpider


def main():
    """
    后端启动入口
    :return:
    """
    spider = TuguaSpider(init_url='http://www.dapenti.com/blog/blog.asp?subjectid=70&name=xilei')
    MAIN_LOOP.run_until_complete(spider.run())
    MAIN_LOOP.close()


if __name__ == '__main__':
    main()

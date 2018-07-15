if __name__ == '__main__':
    from scrapy.cmdline import execute

    import sys
    import os

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute(["scrapy", "crawl", "tugua"])
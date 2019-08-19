import logging
import sys

from loguru import logger
from sentry_sdk.integrations.logging import EventHandler, BreadcrumbHandler

from pixiu.settings import core_env, LOG_TYPE


def init_log():
    logging.getLogger("chardet").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Retrieve context where the logging call occurred, this happens to be in the 6th frame upward
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(record.levelname, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=logging.DEBUG)

    logger.add(EventHandler(), format="{message}", level="ERROR")
    logger.add(BreadcrumbHandler(), format="{message}", level="ERROR")

    if "file" in LOG_TYPE:
        logger.add("logs/spider.log", rotation="1 day", retention="5 days", enqueue=True)

    if core_env == "dev":
        logger.remove(0)
        logger.add(sys.stderr, level="TRACE")

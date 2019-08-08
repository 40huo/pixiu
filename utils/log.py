import sys

from loguru import logger
from sentry_sdk.integrations.logging import EventHandler, BreadcrumbHandler

from pixiu.settings import core_env


def init_log():
    logger.add(EventHandler(), format="{message}", level="ERROR")
    logger.add(BreadcrumbHandler(), format="{message}", level="ERROR")
    if core_env == "dev":
        logger.remove(0)
        logger.add(sys.stderr, level="TRACE")

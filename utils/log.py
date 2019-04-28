import logging
import logging.config
import os
import platform

from pixiu.settings import LOG_TYPE


class Logger(object):
    def __init__(self, logger, filename='logs/pixiu.log'):
        """
        封装一个log类，用来统一获取logger
        :param logger: 传入logger名称，可用__name__代替
        """
        project_path = os.path.dirname(os.path.dirname(__file__))
        log_file = os.path.join(project_path, filename)
        log_dir = os.path.split(log_file)[0]
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        default_log_format = "[%(asctime)s] [%(name)s] [line:%(lineno)s] [%(levelname)s] %(message)s"
        systemd_log_format = "[%(name)s] [line:%(lineno)s] [%(levelname)s] %(message)s"
        datetime_format = "%Y-%m-%d %H:%M:%S"

        logging_dict = {
            'version': 1,
            'disable_existing_loggers': False,  # set True to suppress existing loggers from other modules
            'loggers': {
                '': {
                    'level': 'DEBUG',
                    'handlers': LOG_TYPE,
                },
            },
            'formatters': {
                'colored_console': {
                    '()': 'coloredlogs.ColoredFormatter',  # 使用自定义formatter的工厂类来实例化
                    'format': default_log_format,
                    'datefmt': datetime_format
                },
                'file': {
                    'format': default_log_format,
                    'datefmt': datetime_format
                },
                'systemd': {
                    'format': systemd_log_format,
                    'datefmt': datetime_format,
                },
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'colored_console',
                },
                'file': {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'file',
                    'filename': log_file,
                    'encoding': 'utf-8',
                    'maxBytes': 1024 * 1024 * 5,
                    'backupCount': 5
                },
                'systemd': {
                    'level': 'DEBUG',
                    'class': 'systemd.journal.JournalHandler' if 'linux' in platform.platform().lower() else 'logging.StreamHandler',
                    'formatter': 'systemd'
                }
            },
        }
        logging.config.dictConfig(logging_dict)

        # 减少无用日志
        logging.getLogger('chardet').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

        logger = logging.getLogger(logger)
        self.logger = logger

    def get_logger(self):
        return self.logger

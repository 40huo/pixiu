import logging
import logging.config
import os


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

        log_format = "[%(asctime)s] [%(name)s] [line:%(lineno)s] [%(levelname)s] %(message)s"

        logging_dict = {
            'version': 1,
            'disable_existing_loggers': False,  # set True to suppress existing loggers from other modules
            'loggers': {
                '': {
                    'level': 'DEBUG',
                    'handlers': ['console', 'file'],
                },
            },
            'formatters': {
                'colored_console': {
                    '()': 'coloredlogs.ColoredFormatter',  # 使用自定义formatter的工厂类来实例化
                    'format': log_format,
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'format_for_file': {
                    'format': log_format,
                    'datefmt': '%Y-%m-%d %H:%M:%S'}
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
                    'formatter': 'format_for_file',
                    'filename': log_file,
                    'encoding': 'utf-8',
                    'maxBytes': 1024 * 1024 * 5,
                    'backupCount': 5
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
from .base import LoggerBase
from loguru import logger as loguru_logger


class LoguruLogger(LoggerBase):
    """Loguru适配器"""

    def __init__(self):
        # 可以在这里配置Loguru
        pass

    def info(self, message: str):
        loguru_logger.info(message)

    def error(self, message: str):
        loguru_logger.error(message)
from .base import LoggerBase
import logging


class BuiltinLogger(LoggerBase):
    """内置logging适配器"""

    def __init__(self, name="BruceLogger", level=logging.INFO):
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(name)

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)
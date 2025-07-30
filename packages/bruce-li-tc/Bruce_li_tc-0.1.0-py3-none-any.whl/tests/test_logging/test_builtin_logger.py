import unittest
from bruce_li_tc.logging.builtin_logger import BuiltinLogger
import logging


class TestBuiltinLogger(unittest.TestCase):
    def test_logging(self):
        logger = BuiltinLogger(name="TestLogger")
        logger.info("This is an info message")
        logger.error("This is an error message")

        # 验证日志记录器名称
        self.assertEqual(logger.logger.name, "TestLogger")
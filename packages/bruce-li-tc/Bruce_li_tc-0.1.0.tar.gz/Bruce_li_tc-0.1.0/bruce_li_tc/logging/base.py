from abc import ABC, abstractmethod

class LoggerBase(ABC):
    """日志模块抽象基类"""
    @abstractmethod
    def info(self, message: str):
        pass

    @abstractmethod
    def error(self, message: str):
        pass
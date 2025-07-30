from .logging.builtin_logger import BuiltinLogger
from .logging.loguru_logger import LoguruLogger
from .http.requests_client import RequestsClient
from .http.urllib_client import UrllibClient
from .http.aiohttp_client import AiohttpClient
from .table.csv_handler import CSVHandler
from .table.excel_handler import ExcelHandler


class LoggerFactory:
    """日志工厂"""
    _loggers = {
        'builtin': BuiltinLogger,
        'loguru': LoguruLogger
    }

    @staticmethod
    def create(logger_type: str = 'builtin', **kwargs) -> 'LoggerBase':
        if logger_type not in LoggerFactory._loggers:
            raise ValueError(f"Unsupported logger type: {logger_type}")
        return LoggerFactory._loggers[logger_type](**kwargs)


class HttpClientFactory:
    """HTTP客户端工厂"""
    _clients = {
        'requests': RequestsClient,
        'urllib': UrllibClient,
        'aiohttp': AiohttpClient
    }

    @staticmethod
    def create(client_type: str = 'requests', **kwargs) -> 'HttpClientBase':
        if client_type not in HttpClientFactory._clients:
            raise ValueError(f"Unsupported HTTP client type: {client_type}")
        return HttpClientFactory._clients[client_type](**kwargs)


class TableHandlerFactory:
    """表格处理工厂"""
    _handlers = {
        'csv': CSVHandler,
        'excel': ExcelHandler
    }

    @staticmethod
    def create(handler_type: str = 'csv', **kwargs) -> 'TableHandlerBase':
        if handler_type not in TableHandlerFactory._handlers:
            raise ValueError(f"Unsupported table handler type: {handler_type}")
        return TableHandlerFactory._handlers[handler_type](**kwargs)
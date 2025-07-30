from datetime import datetime


class TimeUtils:
    """时间工具类"""

    @staticmethod
    def now_str(format: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.now().strftime(format)

    @staticmethod
    def parse(date_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        return datetime.strptime(date_str, format)

    @staticmethod
    def format(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        return dt.strftime(format)
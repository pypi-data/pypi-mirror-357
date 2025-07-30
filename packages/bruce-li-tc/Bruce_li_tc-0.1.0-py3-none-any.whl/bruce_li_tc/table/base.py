from abc import ABC, abstractmethod
from typing import List, Dict


class TableHandlerBase(ABC):
    """表格处理抽象基类"""

    @abstractmethod
    def write(self, data: List[Dict], file_path: str):
        pass

    @abstractmethod
    def read(self, file_path: str) -> List[Dict]:
        pass
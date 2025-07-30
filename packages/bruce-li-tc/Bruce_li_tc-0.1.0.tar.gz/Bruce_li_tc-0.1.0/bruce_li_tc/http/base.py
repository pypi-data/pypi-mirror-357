from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class HttpClientBase(ABC):
    """HTTP客户端抽象基类"""

    @abstractmethod
    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def post(self, url: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        pass
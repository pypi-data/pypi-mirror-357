from .base import HttpClientBase
import requests


class RequestsClient(HttpClientBase):
    """Requests适配器"""

    def __init__(self, session=None):
        self.session = session or requests.Session()

    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        response = self.session.get(url, **kwargs)
        return self._format_response(response)

    def post(self, url: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        response = self.session.post(url, data=data, **kwargs)
        return self._format_response(response)

    def _format_response(self, response):
        """格式化响应为统一格式"""
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content': response.content.decode('utf-8'),
            'json': response.json() if response.headers.get('Content-Type') == 'application/json' else None
        }
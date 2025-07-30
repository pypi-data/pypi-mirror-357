from .base import HttpClientBase
import urllib.request
import urllib.parse
import json
from http.client import HTTPResponse


class UrllibClient(HttpClientBase):
    """urllib适配器"""

    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        req = urllib.request.Request(url, headers=kwargs.get('headers', {}))
        with urllib.request.urlopen(req) as response:
            return self._process_response(response)

    def post(self, url: str, data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        headers = kwargs.get('headers', {})
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        encoded_data = urllib.parse.urlencode(data or {}).encode('utf-8')
        req = urllib.request.Request(url, data=encoded_data, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            return self._process_response(response)

    def _process_response(self, response: HTTPResponse):
        """处理响应并返回统一格式"""
        content = response.read().decode('utf-8')
        return {
            'status_code': response.status,
            'headers': dict(response.headers),
            'content': content,
            'json': json.loads(content) if 'application/json' in response.headers.get('Content-Type', '') else None
        }
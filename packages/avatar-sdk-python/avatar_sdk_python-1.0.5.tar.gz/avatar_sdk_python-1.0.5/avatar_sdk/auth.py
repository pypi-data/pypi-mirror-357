"""
虚拟人认证模块
"""

import base64
import hashlib
import hmac
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

from .exceptions import AvatarAuthException


class AvatarAuth:
    """虚拟人认证类"""

    @staticmethod
    def sha256base64(data: bytes) -> str:
        """计算SHA256并编码为base64"""
        sha256 = hashlib.sha256()
        sha256.update(data)
        digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
        return digest

    @staticmethod
    def parse_url(request_url: str) -> tuple:
        """解析URL，返回(host, path, schema)"""
        try:
            stidx = request_url.index("://")
            host = request_url[stidx + 3:]
            schema = request_url[:stidx + 3]
            edidx = host.index("/")
            if edidx <= 0:
                raise AvatarAuthException(
                    f"Invalid request URL: {request_url}")
            path = host[edidx:]
            host = host[:edidx]
            return host, path, schema
        except (ValueError, IndexError) as e:
            raise AvatarAuthException(
                f"Failed to parse URL: {request_url}") from e

    @staticmethod
    def build_auth_url(request_url: str, method: str = "GET",
                       api_key: str = "", api_secret: str = "") -> str:
        """构建认证URL"""
        try:
            host, path, schema = AvatarAuth.parse_url(request_url)

            now = datetime.now()
            date = format_date_time(mktime(now.timetuple()))

            signature_origin = f"host: {host}\ndate: {date}\n{method} {path} HTTP/1.1"
            signature_sha = hmac.new(
                api_secret.encode('utf-8'),
                signature_origin.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
            signature_sha = base64.b64encode(
                signature_sha).decode(encoding='utf-8')

            authorization_origin = (
                f'api_key="{api_key}", algorithm="hmac-sha256", '
                f'headers="host date request-line", signature="{signature_sha}"'
            )
            authorization = base64.b64encode(
                authorization_origin.encode('utf-8')
            ).decode(encoding='utf-8')

            values = {
                "host": host,
                "date": date,
                "authorization": authorization
            }

            return request_url + "?" + urlencode(values)

        except Exception as e:
            raise AvatarAuthException(
                f"Failed to build auth URL: {str(e)}") from e

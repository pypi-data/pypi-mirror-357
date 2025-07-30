from typing import Dict
from .models import DownloadRequest

def create_download_request(name: str, url: str, file_path: str = "", 
                          segments: int = 8, priority: int = 0,
                          headers: Dict[str, str] = None,
                          cookies: Dict[str, str] = None,
                          proxy: str = None, max_retries: int = 3,
                          timeout: float = 30.0, 
                          speed_limit: int = None,
                          ftp_username: str = None,
                          ftp_password: str = None,
                          ftp_passive: bool = True,
                          checksum: str = None,
                          checksum_type: str = "md5") -> DownloadRequest:
    return DownloadRequest(
        name=name,
        url=url,
        file_path=file_path,
        segments=segments,
        priority=priority,
        headers=headers or {},
        cookies=cookies or {},
        proxy=proxy,
        max_retries=max_retries,
        timeout=timeout,
        speed_limit=speed_limit,
        ftp_username=ftp_username,
        ftp_password=ftp_password,
        ftp_passive=ftp_passive,
        checksum=checksum,
        checksum_type=checksum_type
    )

def cookies_from_requests_session(session: 'requests.Session') -> Dict[str, str]:
    return {cookie.name: cookie.value for cookie in session.cookies}

def headers_from_requests_session(session: 'requests.Session') -> Dict[str, str]:
    return dict(session.headers)
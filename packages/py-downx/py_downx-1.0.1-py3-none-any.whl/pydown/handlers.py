import asyncio
import threading
import time
import hashlib
import os
import pickle
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import httpx

from .models import DownloadRequest, DownloadStatus
from .observers import DownloadObserver

logger = logging.getLogger(__name__)

class SegmentDownloader:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
    
    async def download_segment(self, url: str, start: int, end: int, 
                             headers: Dict[str, str] = None,
                             timeout: float = 30.0) -> bytes:
        if headers is None:
            headers = {}
        
        headers['Range'] = f'bytes={start}-{end}'
        
        async with self.client.stream('GET', url, headers=headers, timeout=timeout) as response:
            response.raise_for_status()
            
            content = b''
            async for chunk in response.aiter_bytes():
                content += chunk
            
            return content
    
    async def get_content_length(self, url: str, headers: Dict[str, str] = None,
                               timeout: float = 30.0) -> Optional[int]:
        if headers is None:
            headers = {}
        
        async with self.client.stream('HEAD', url, headers=headers, timeout=timeout) as response:
            if response.status_code == 200:
                content_length = response.headers.get('content-length')
                return int(content_length) if content_length else None
        return None

class SpeedLimiter:
    def __init__(self, max_speed_bps: int):
        self.max_speed_bps = max_speed_bps
        self.last_update = time.time()
        self.bytes_transferred = 0
        self._lock = threading.Lock()
    
    def throttle(self, bytes_count: int) -> None:
        if self.max_speed_bps <= 0:
            return
        
        with self._lock:
            current_time = time.time()
            self.bytes_transferred += bytes_count
            
            elapsed = current_time - self.last_update
            if elapsed >= 1.0:
                expected_bytes = self.max_speed_bps * elapsed
                if self.bytes_transferred > expected_bytes:
                    sleep_time = (self.bytes_transferred - expected_bytes) / self.max_speed_bps
                    time.sleep(sleep_time)
                
                self.last_update = current_time
                self.bytes_transferred = 0

class RetryHandler:
    def __init__(self, max_retries: int = 3, initial_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
    
    def should_retry(self, request: DownloadRequest, error: Exception) -> bool:

        if request.retry_count >= request.max_retries:
            return False
        

        retryable_errors = (
            ConnectionError, TimeoutError, OSError,
            httpx.ConnectTimeout, httpx.ReadTimeout, httpx.NetworkError
        )
        
        if isinstance(error, retryable_errors):
            return True
        

        if hasattr(error, 'response'):
            status_code = getattr(error.response, 'status_code', None)
            if status_code:

                if status_code >= 500 or status_code == 429:
                    return True
        
        return False
    
    def get_retry_delay(self, request: DownloadRequest) -> float:

        delay = request.retry_delay * (2 ** request.retry_count)
        return min(delay, self.max_delay)
    
    async def execute_with_retry(self, request: DownloadRequest, download_func, observer):

        last_error = None
        
        while request.retry_count <= request.max_retries:
            try:
                return await download_func(request, observer)
            except Exception as e:
                last_error = e
                
                if not self.should_retry(request, e):
                    raise e
                
                request.retry_count += 1
                if request.retry_count <= request.max_retries:
                    delay = self.get_retry_delay(request)
                    logger.warning(f"Download {request.name} failed, retrying in {delay}s (attempt {request.retry_count}/{request.max_retries})")
                    await asyncio.sleep(delay)
                else:
                    raise e
        
        raise last_error

class ChecksumValidator:
    @staticmethod
    def calculate_checksum(file_path: str, checksum_type: str = "md5") -> str:

        hash_func = {
            'md5': hashlib.md5(),
            'sha1': hashlib.sha1(),
            'sha256': hashlib.sha256()
        }.get(checksum_type.lower())
        
        if not hash_func:
            raise ValueError(f"Unsupported checksum type: {checksum_type}")
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def verify_checksum(file_path: str, expected_checksum: str, checksum_type: str = "md5") -> bool:

        if not expected_checksum:
            return True
        
        try:
            actual_checksum = ChecksumValidator.calculate_checksum(file_path, checksum_type)
            return actual_checksum.lower() == expected_checksum.lower()
        except Exception:
            return False

class ResumeHandler:
    @staticmethod
    def can_resume(request: DownloadRequest) -> bool:

        if not request.resume_supported:
            return False
        
        partial_path = request.partial_file_path or f"{request.file_path}.partial"
        return os.path.exists(partial_path) and os.path.getsize(partial_path) > 0
    
    @staticmethod
    def get_resume_position(request: DownloadRequest) -> int:

        partial_path = request.partial_file_path or f"{request.file_path}.partial"
        if os.path.exists(partial_path):
            return os.path.getsize(partial_path)
        return 0
    
    @staticmethod
    def setup_partial_download(request: DownloadRequest) -> str:
        partial_path = request.partial_file_path or f"{request.file_path}.partial"
        

        Path(partial_path).parent.mkdir(parents=True, exist_ok=True)
        
        return partial_path
    
    @staticmethod
    def finalize_download(request: DownloadRequest) -> bool:
        partial_path = request.partial_file_path or f"{request.file_path}.partial"
        
        if os.path.exists(partial_path):

            if request.checksum:
                if not ChecksumValidator.verify_checksum(partial_path, request.checksum, request.checksum_type):
                    logger.error(f"Checksum verification failed for {request.name}")
                    return False
            
            os.rename(partial_path, request.file_path)
            return True
        
        return False

class DuplicateHandler:
    def __init__(self, strategy: str = "skip"):
        self.strategy = strategy
        self.downloaded_files: Dict[str, Dict[str, Any]] = {}
    
    def check_duplicate(self, request: DownloadRequest) -> bool:


        download_key = self._get_download_key(request)
        
        if download_key in self.downloaded_files:
            existing_info = self.downloaded_files[download_key]
            
            if self.strategy == "skip":

                if self._is_file_valid(existing_info):
                    request.status = DownloadStatus.DUPLICATE
                    return True
                else:

                    del self.downloaded_files[download_key]
                    return False
            
            elif self.strategy == "overwrite":

                if 'file_path' in existing_info and os.path.exists(existing_info['file_path']):
                    try:
                        os.remove(existing_info['file_path'])
                    except OSError:
                        pass
                del self.downloaded_files[download_key]
                return False
            
            elif self.strategy == "rename":
                request.file_path = self._get_unique_filename(request.file_path)
                return False
            
            elif self.strategy == "resume":

                if ResumeHandler.can_resume(request):
                    return False
                else:
                    request.status = DownloadStatus.DUPLICATE
                    return True
        

        self.downloaded_files[download_key] = {
            'url': request.url,
            'file_path': request.file_path,
            'timestamp': time.time(),
            'checksum': request.checksum,
            'file_size': request.file_size
        }
        
        return False
    
    def _get_download_key(self, request: DownloadRequest) -> str:


        key_data = f"{request.url}_{request.file_size}_{request.checksum or ''}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_file_valid(self, file_info: Dict[str, Any]) -> bool:

        file_path = file_info.get('file_path')
        if not file_path or not os.path.exists(file_path):
            return False
        

        expected_size = file_info.get('file_size', 0)
        if expected_size > 0:
            actual_size = os.path.getsize(file_path)
            if actual_size != expected_size:
                return False
        

        expected_checksum = file_info.get('checksum')
        if expected_checksum:
            return ChecksumValidator.verify_checksum(file_path, expected_checksum)
        
        return True
    
    def _get_unique_filename(self, file_path: str) -> str:

        path = Path(file_path)
        counter = 1
        while path.exists():
            stem = path.stem

            if stem.endswith(f"_{counter-1}") and counter > 1:
                stem = stem[:-len(f"_{counter-1}")]
            new_name = f"{stem}_{counter}{path.suffix}"
            path = path.parent / new_name
            counter += 1
        return str(path)
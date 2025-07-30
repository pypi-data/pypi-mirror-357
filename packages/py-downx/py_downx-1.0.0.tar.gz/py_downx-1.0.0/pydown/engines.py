import asyncio
import threading
import time
import logging
import ftplib
import paramiko
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from pathlib import Path
from typing import Dict, Optional
import httpx

from .models import DownloadRequest, DownloadStatus, ProgressInfo
from .observers import DownloadObserver
from .handlers import RetryHandler, SpeedLimiter, ResumeHandler, ChecksumValidator

logger = logging.getLogger(__name__)

class DownloadEngine(ABC):
    @abstractmethod
    async def download(self, request: DownloadRequest, observer: DownloadObserver) -> bool:
        pass
    
    @abstractmethod
    def pause(self, request: DownloadRequest) -> bool:
        pass
    
    @abstractmethod
    def resume(self, request: DownloadRequest) -> bool:
        pass

class HTTPDownloadEngine(DownloadEngine):
    def __init__(self, max_segments: int = 8):
        self.max_segments = max_segments
        self.active_downloads: Dict[str, bool] = {}
        self.paused_downloads: Dict[str, bool] = {}
        self._lock = threading.Lock()
        self.retry_handler = RetryHandler()
    
    async def download(self, request: DownloadRequest, observer: DownloadObserver) -> bool:

        return await self.retry_handler.execute_with_retry(
            request, self._download_with_resume, observer
        )
    
    async def _download_with_resume(self, request: DownloadRequest, observer: DownloadObserver) -> bool:
        try:
            with self._lock:
                self.active_downloads[request.url] = True
                self.paused_downloads[request.url] = False
            
            old_status = request.status
            request.status = DownloadStatus.IN_PROGRESS
            observer.on_status_change(request, old_status, request.status)
            

            resume_position = 0
            partial_path = ResumeHandler.setup_partial_download(request)
            
            if ResumeHandler.can_resume(request):
                resume_position = ResumeHandler.get_resume_position(request)
                request.downloaded_size = resume_position
                logger.info(f"Resuming download {request.name} from position {resume_position}")
            
            client_config = {
                'timeout': httpx.Timeout(request.timeout),
                'verify': False,
                'follow_redirects': True,
                'limits': httpx.Limits(max_keepalive_connections=20, max_connections=100)
            }
            
            if request.proxy:
                client_config['proxies'] = request.proxy
            

            cookies_jar = httpx.Cookies()
            for name, value in request.cookies.items():
                cookies_jar.set(name, value)
            
            client_config['cookies'] = cookies_jar
            
            async with httpx.AsyncClient(**client_config) as client:

                try:
                    head_response = await client.head(request.url, headers=request.headers)
                    content_length = head_response.headers.get('content-length')
                    if content_length:
                        request.file_size = int(content_length)
                        supports_ranges = 'bytes' in head_response.headers.get('accept-ranges', '')
                        
                        if supports_ranges and request.file_size > 1024 * 1024 and resume_position == 0:
                            return await self._download_with_segments_resume(
                                request, observer, client, partial_path, resume_position
                            )
                except:
                    pass
                
                return await self._download_single_stream_resume(
                    request, observer, client, partial_path, resume_position
                )
        
        except Exception as e:
            observer.on_error(request, e)
            request.status = DownloadStatus.FAILED
            request.error_message = str(e)
            raise e
        finally:
            with self._lock:
                self.active_downloads.pop(request.url, None)
                self.paused_downloads.pop(request.url, None)
    
    async def _download_single_stream_resume(self, request: DownloadRequest,
                                           observer: DownloadObserver,
                                           client: httpx.AsyncClient,
                                           partial_path: str,
                                           resume_position: int) -> bool:

        speed_limiter = SpeedLimiter(request.speed_limit or 0)
        start_time = time.time()
        

        headers = request.headers.copy()
        if resume_position > 0:
            headers['Range'] = f'bytes={resume_position}-'
        
        file_mode = 'ab' if resume_position > 0 else 'wb'
        
        async with client.stream('GET', request.url, headers=headers) as response:
            response.raise_for_status()
            

            if not request.file_size:
                content_length = response.headers.get('content-length')
                if content_length:
                    request.file_size = int(content_length) + resume_position
            
            with open(partial_path, file_mode) as f:
                async for chunk in response.aiter_bytes():
                    if self._is_paused(request.url):
                        return False
                    
                    f.write(chunk)
                    request.downloaded_size += len(chunk)
                    
                    if request.speed_limit:
                        speed_limiter.throttle(len(chunk))
                    
                    elapsed_time = time.time() - start_time
                    speed = request.downloaded_size / elapsed_time if elapsed_time > 0 else 0
                    
                    if request.file_size > 0:
                        request.progress = (request.downloaded_size / request.file_size) * 100
                    
                    progress_info = ProgressInfo(
                        total_size=request.file_size,
                        downloaded_size=request.downloaded_size,
                        speed=speed,
                        eta=(request.file_size - request.downloaded_size) / speed if speed > 0 and request.file_size > 0 else 0,
                        elapsed_time=elapsed_time,
                        progress_percent=request.progress
                    )
                    
                    observer.on_progress(request, progress_info)
        

        if ResumeHandler.finalize_download(request):
            request.status = DownloadStatus.COMPLETED
            return True
        else:
            request.status = DownloadStatus.FAILED
            request.error_message = "Checksum verification failed"
            return False
    
    def pause(self, request: DownloadRequest) -> bool:
        with self._lock:
            self.paused_downloads[request.url] = True
            old_status = request.status
            request.status = DownloadStatus.PAUSED
        return True
    
    def resume(self, request: DownloadRequest) -> bool:
        with self._lock:
            self.paused_downloads[request.url] = False
            old_status = request.status
            request.status = DownloadStatus.PENDING
        return True
    
    def _is_paused(self, url: str) -> bool:
        return self.paused_downloads.get(url, False)

class FTPDownloadEngine(DownloadEngine):
    def __init__(self):
        self.active_downloads: Dict[str, bool] = {}
        self.paused_downloads: Dict[str, bool] = {}
        self._lock = threading.Lock()
        self.retry_handler = RetryHandler()
    
    async def download(self, request: DownloadRequest, observer: DownloadObserver) -> bool:
        return await self.retry_handler.execute_with_retry(
            request, self._download_ftp_with_resume, observer
        )
    
    async def _download_ftp_with_resume(self, request: DownloadRequest, observer: DownloadObserver) -> bool:
        try:
            with self._lock:
                self.active_downloads[request.url] = True
                self.paused_downloads[request.url] = False
            
            old_status = request.status
            request.status = DownloadStatus.IN_PROGRESS
            observer.on_status_change(request, old_status, request.status)
            

            parsed = urlparse(request.url)
            host = parsed.hostname
            port = parsed.port or 21
            username = request.ftp_username or parsed.username or 'anonymous'
            password = request.ftp_password or parsed.password or 'anonymous@'
            remote_path = parsed.path
            
            if not host:
                raise ValueError("Invalid FTP URL: missing hostname")
            

            partial_path = ResumeHandler.setup_partial_download(request)
            resume_position = 0
            
            if ResumeHandler.can_resume(request):
                resume_position = ResumeHandler.get_resume_position(request)
                request.downloaded_size = resume_position
                logger.info(f"Resuming FTP download {request.name} from position {resume_position}")
            

            success = await asyncio.get_event_loop().run_in_executor(
                None, self._download_ftp_file, 
                host, port, username, password, remote_path, request, observer, partial_path, resume_position
            )
            
            if success:

                if ResumeHandler.finalize_download(request):
                    request.status = DownloadStatus.COMPLETED
                    return True
                else:
                    request.status = DownloadStatus.FAILED
                    request.error_message = "File finalization failed"
                    return False
            else:
                return False
            
        except Exception as e:
            observer.on_error(request, e)
            request.status = DownloadStatus.FAILED
            request.error_message = str(e)
            raise e
        finally:
            with self._lock:
                self.active_downloads.pop(request.url, None)
                self.paused_downloads.pop(request.url, None)
    
    def _download_ftp_file(self, host: str, port: int, username: str, password: str, 
                          remote_path: str, request: DownloadRequest, observer: DownloadObserver,
                          partial_path: str, resume_position: int) -> bool:
        
        ftp = None
        try:
            ftp = ftplib.FTP()
            ftp.connect(host, port, timeout=request.timeout)
            ftp.login(username, password)
            
            if request.ftp_passive:
                ftp.set_pasv(True)
            

            try:
                file_size = ftp.size(remote_path)
                if file_size:
                    request.file_size = file_size
            except ftplib.error_perm:

                request.file_size = 0
            
            speed_limiter = SpeedLimiter(request.speed_limit or 0)
            start_time = time.time()
            

            file_mode = 'ab' if resume_position > 0 else 'wb'
            

            if resume_position > 0:
                try:
                    ftp.voidcmd(f'REST {resume_position}')
                except ftplib.error_perm:

                    resume_position = 0
                    request.downloaded_size = 0
                    file_mode = 'wb'
            
            with open(partial_path, file_mode) as f:
                def write_callback(data):
                    if self._is_paused(request.url):
                        raise ftplib.error_temp("Download paused")
                    
                    f.write(data)
                    request.downloaded_size += len(data)
                    
                    if request.speed_limit:
                        speed_limiter.throttle(len(data))
                    

                    if request.file_size > 0:
                        request.progress = (request.downloaded_size / request.file_size) * 100
                    
                    elapsed_time = time.time() - start_time
                    speed = (request.downloaded_size - resume_position) / elapsed_time if elapsed_time > 0 else 0
                    eta = (request.file_size - request.downloaded_size) / speed if speed > 0 and request.file_size > 0 else 0
                    
                    progress_info = ProgressInfo(
                        total_size=request.file_size,
                        downloaded_size=request.downloaded_size,
                        speed=speed,
                        eta=eta,
                        elapsed_time=elapsed_time,
                        progress_percent=request.progress
                    )
                    
                    observer.on_progress(request, progress_info)
                

                try:
                    ftp.retrbinary(f'RETR {remote_path}', write_callback)
                except ftplib.error_temp as e:
                    if "paused" in str(e):
                        return False
                    raise
            
            return True
            
        except Exception as e:
            logger.error(f"FTP download error: {e}")
            observer.on_error(request, e)
            return False
        finally:
            if ftp:
                try:
                    ftp.quit()
                except:
                    try:
                        ftp.close()
                    except:
                        pass
    
    def pause(self, request: DownloadRequest) -> bool:
        with self._lock:
            self.paused_downloads[request.url] = True
            request.status = DownloadStatus.PAUSED
        return True
    
    def resume(self, request: DownloadRequest) -> bool:
        with self._lock:
            self.paused_downloads[request.url] = False
            request.status = DownloadStatus.PENDING
        return True
    
    def _is_paused(self, url: str) -> bool:
        return self.paused_downloads.get(url, False)

class SFTPDownloadEngine(DownloadEngine):
    def __init__(self):
        self.active_downloads: Dict[str, bool] = {}
        self.paused_downloads: Dict[str, bool] = {}
        self._lock = threading.Lock()
    
    async def download(self, request: DownloadRequest, observer: DownloadObserver) -> bool:
        try:
            with self._lock:
                self.active_downloads[request.url] = True
                self.paused_downloads[request.url] = False
            
            old_status = request.status
            request.status = DownloadStatus.IN_PROGRESS
            observer.on_status_change(request, old_status, request.status)
            

            parsed = urlparse(request.url)
            host = parsed.hostname
            port = parsed.port or 22
            username = request.ftp_username or parsed.username
            password = request.ftp_password or parsed.password
            remote_path = parsed.path
            
            if not username:
                raise ValueError("SFTP requires username")
            

            Path(request.file_path).parent.mkdir(parents=True, exist_ok=True)
            

            return await asyncio.get_event_loop().run_in_executor(
                None, self._download_sftp_file, 
                host, port, username, password, remote_path, request, observer
            )
            
        except Exception as e:
            observer.on_error(request, e)
            request.status = DownloadStatus.FAILED
            request.error_message = str(e)
            return False
        finally:
            with self._lock:
                self.active_downloads.pop(request.url, None)
                self.paused_downloads.pop(request.url, None)
    
    def _download_sftp_file(self, host: str, port: int, username: str, password: str,
                           remote_path: str, request: DownloadRequest, observer: DownloadObserver) -> bool:
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(host, port=port, username=username, password=password, timeout=request.timeout)
            sftp = ssh.open_sftp()
            

            try:
                file_attrs = sftp.stat(remote_path)
                request.file_size = file_attrs.st_size
            except:
                request.file_size = 0
            
            speed_limiter = SpeedLimiter(request.speed_limit or 0)
            start_time = time.time()
            

            with sftp.open(remote_path, 'rb') as remote_file:
                with open(request.file_path, 'wb') as local_file:
                    while True:
                        if self._is_paused(request.url):
                            return False
                        
                        chunk = remote_file.read(8192)  
                        if not chunk:
                            break
                        
                        local_file.write(chunk)
                        request.downloaded_size += len(chunk)
                        
                        if request.speed_limit:
                            speed_limiter.throttle(len(chunk))
                        
                        if request.file_size > 0:
                            request.progress = (request.downloaded_size / request.file_size) * 100
                        
                        elapsed_time = time.time() - start_time
                        speed = request.downloaded_size / elapsed_time if elapsed_time > 0 else 0
                        eta = (request.file_size - request.downloaded_size) / speed if speed > 0 and request.file_size > 0 else 0
                        
                        progress_info = ProgressInfo(
                            total_size=request.file_size,
                            downloaded_size=request.downloaded_size,
                            speed=speed,
                            eta=eta,
                            elapsed_time=elapsed_time,
                            progress_percent=request.progress
                        )
                        
                        observer.on_progress(request, progress_info)
            
            request.status = DownloadStatus.COMPLETED
            return True
            
        finally:
            try:
                ssh.close()
            except:
                pass
    
    def pause(self, request: DownloadRequest) -> bool:
        with self._lock:
            self.paused_downloads[request.url] = True
            request.status = DownloadStatus.PAUSED
        return True
    
    def resume(self, request: DownloadRequest) -> bool:
        with self._lock:
            self.paused_downloads[request.url] = False
            request.status = DownloadStatus.PENDING
        return True
    
    def _is_paused(self, url: str) -> bool:
        return self.paused_downloads.get(url, False)
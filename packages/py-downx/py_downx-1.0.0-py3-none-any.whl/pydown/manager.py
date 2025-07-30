import asyncio
import threading
import multiprocessing
import time
import json
import logging
import traceback
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Optional, Set
from queue import PriorityQueue
import validators

from .models import DownloadRequest, DownloadStatus
from .observers import DownloadObserver, LoggingObserver, CompositeObserver
from .engines import DownloadEngine, HTTPDownloadEngine, FTPDownloadEngine, SFTPDownloadEngine
from .handlers import DuplicateHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DownloadQueue:
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.queue = PriorityQueue()
        self.active_downloads: Set[str] = set()
        self.paused_downloads: Set[str] = set()
        self._lock = threading.Lock()
    
    def add(self, request: DownloadRequest) -> None:
        priority = -request.priority
        self.queue.put((priority, id(request), request))
    
    def get_next(self) -> Optional[DownloadRequest]:
        with self._lock:
            if len(self.active_downloads) >= self.max_concurrent:
                return None
            
            while not self.queue.empty():
                _, _, request = self.queue.get()
                if request.url not in self.paused_downloads and request.url not in self.active_downloads:
                    self.active_downloads.add(request.url)
                    return request
        
        return None
    
    def mark_completed(self, request: DownloadRequest) -> None:
        with self._lock:
            self.active_downloads.discard(request.url)
    
    def pause(self, request: DownloadRequest) -> bool:
        with self._lock:
            self.paused_downloads.add(request.url)
            self.active_downloads.discard(request.url)
        return True
    
    def resume(self, request: DownloadRequest) -> bool:
        with self._lock:
            self.paused_downloads.discard(request.url)
        self.add(request)
        return True
    
    def is_empty(self) -> bool:
        return self.queue.empty() and len(self.active_downloads) == 0

class DownloadManager:
    def __init__(self, 
                 max_concurrent_downloads: int = 3,
                 max_segments_per_download: int = 8,
                 max_workers: Optional[int] = None,
                 use_multiprocessing: bool = True,
                 duplicate_strategy: str = "skip",
                 log_file: Optional[str] = None,
                 quiet: bool = False):
        
        self.max_concurrent_downloads = max_concurrent_downloads
        self.max_segments_per_download = max_segments_per_download
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.use_multiprocessing = use_multiprocessing
        self.quiet = quiet
        
        self.download_queue = DownloadQueue(max_concurrent_downloads)
        self.http_engine = HTTPDownloadEngine(max_segments_per_download)
        self.ftp_engine = FTPDownloadEngine()
        self.sftp_engine = SFTPDownloadEngine()
        self.duplicate_handler = DuplicateHandler(duplicate_strategy)
        
        self.observers: List[DownloadObserver] = []
        if not quiet:
            self.observers.append(LoggingObserver())
        
        self.downloads: Dict[str, DownloadRequest] = {}
        self._running = False
        self._executor = None
        

        self._configure_logging(log_file, quiet)
    
    def _get_download_engine(self, url: str) -> DownloadEngine:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        
        if scheme in ['http', 'https']:
            return self.http_engine
        elif scheme == 'ftp':
            return self.ftp_engine
        elif scheme in ['sftp', 'ftps']:
            return self.sftp_engine
        else:
            raise ValueError(f"Unsupported protocol: {scheme}")
    
    def _configure_logging(self, log_file: Optional[str], quiet: bool) -> None:
        

        loggers_to_configure = [
            logging.getLogger(__name__),
            logging.getLogger('httpx'),
            logging.getLogger('httpcore'),
            logging.getLogger('urllib3'),
            logging.getLogger('requests')
        ]
        
        if quiet:
            for logger_obj in loggers_to_configure:
                logger_obj.setLevel(logging.CRITICAL)
                for handler in logger_obj.handlers[:]:
                    logger_obj.removeHandler(handler)
                logger_obj.propagate = False
        else:
            for logger_obj in loggers_to_configure:
                logger_obj.setLevel(logging.INFO)
        

        if log_file:
            self._setup_file_logging(log_file, loggers_to_configure)
    
    def _setup_file_logging(self, log_file: str, loggers_to_configure: List[logging.Logger]) -> None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        for logger_obj in loggers_to_configure:
            logger_obj.addHandler(file_handler)
            logger_obj.setLevel(logging.INFO)
            logger_obj.propagate = False  
    
    def add_observer(self, observer: DownloadObserver) -> None:
        self.observers.append(observer)
    
    def remove_observer(self, observer: DownloadObserver) -> None:
        if observer in self.observers:
            self.observers.remove(observer)
    
    def add_download(self, request: DownloadRequest) -> str:
        if not validators.url(request.url):
            raise ValueError(f"Invalid URL: {request.url}")
        
        if not request.file_path:
            parsed_url = urlparse(request.url)
            filename = Path(parsed_url.path).name or "download"
            request.file_path = str(Path.cwd() / filename)
        
        if self.duplicate_handler.check_duplicate(request):
            return request.url
        
        self.downloads[request.url] = request
        self.download_queue.add(request)
        
        return request.url
    
    def add_downloads_from_json(self, json_file: str) -> List[str]:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        download_ids = []
        for item in data:
            if isinstance(item, dict):
                request = DownloadRequest.from_dict(item)
                download_ids.append(self.add_download(request))
        
        return download_ids
    
    def pause_download(self, url: str) -> bool:
        if url in self.downloads:
            request = self.downloads[url]
            engine = self._get_download_engine(url)
            success = engine.pause(request)
            if success:
                self.download_queue.pause(request)
            return success
        return False
    
    def resume_download(self, url: str) -> bool:
        if url in self.downloads:
            request = self.downloads[url]
            engine = self._get_download_engine(url)
            success = engine.resume(request)
            if success:
                self.download_queue.resume(request)
            return success
        return False
    
    def cancel_download(self, url: str) -> bool:
        if url in self.downloads:
            request = self.downloads[url]
            old_status = request.status
            request.status = DownloadStatus.CANCELLED
            
            for observer in self.observers:
                observer.on_status_change(request, old_status, request.status)
            
            return True
        return False
    
    def get_download_status(self, url: str) -> Optional[DownloadRequest]:
        return self.downloads.get(url)
    
    def get_all_downloads(self) -> Dict[str, DownloadRequest]:
        return self.downloads.copy()
    
    async def _worker(self) -> None:
        while self._running:
            request = self.download_queue.get_next()
            
            if request is None:
                await asyncio.sleep(0.1)
                continue
            
            if self.download_queue.is_empty():
                break
            
            try:
                composite_observer = CompositeObserver(self.observers)

                engine = self._get_download_engine(request.url)
                success = await engine.download(request, composite_observer)
                
                if success:
                    logger.info(f"Download completed: {request.name}")
                else:
                    logger.warning(f"Download failed: {request.name}")
            
            except Exception as e:
                logger.error(f"Worker error for {request.name}: {e}")
                logger.error(traceback.format_exc())
                request.status = DownloadStatus.FAILED
                request.error_message = str(e)
            
            finally:
                self.download_queue.mark_completed(request)
    
    def start(self) -> None:
        if self._running:
            return
        
        self._running = True
        
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        def run_worker_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._worker())
            finally:
                loop.close()
        
        for _ in range(self.max_workers):
            self._executor.submit(run_worker_thread)
    
    def stop(self) -> None:
        self._running = False
        
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None
    
    def wait_for_completion(self) -> None:
        while self._running and not self.download_queue.is_empty():
            time.sleep(0.5)
        
        
        time.sleep(1)
    
    def export_downloads(self, json_file: str) -> None:
        data = [request.to_dict() for request in self.downloads.values()]
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
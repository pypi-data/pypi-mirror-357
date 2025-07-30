import logging
import traceback
from abc import ABC, abstractmethod
from typing import List

from .models import DownloadRequest, ProgressInfo, DownloadStatus

logger = logging.getLogger(__name__)

class DownloadObserver(ABC):
    @abstractmethod
    def on_progress(self, request: DownloadRequest, progress: ProgressInfo) -> None:
        pass
    
    @abstractmethod
    def on_status_change(self, request: DownloadRequest, old_status: DownloadStatus, new_status: DownloadStatus) -> None:
        pass
    
    @abstractmethod
    def on_error(self, request: DownloadRequest, error: Exception) -> None:
        pass

class LoggingObserver(DownloadObserver):
    def on_progress(self, request: DownloadRequest, progress: ProgressInfo) -> None:
        logger.info(f"Download {request.name}: {progress}")
    
    def on_status_change(self, request: DownloadRequest, old_status: DownloadStatus, new_status: DownloadStatus) -> None:
        logger.info(f"Download {request.name}: {old_status.name} -> {new_status.name}")
    
    def on_error(self, request: DownloadRequest, error: Exception) -> None:
        logger.error(f"Download {request.name} error: {error}")
        logger.error(traceback.format_exc())

class CompositeObserver(DownloadObserver):
    def __init__(self, observers: List[DownloadObserver]):
        self.observers = observers
    
    def on_progress(self, request: DownloadRequest, progress: ProgressInfo) -> None:
        for observer in self.observers:
            observer.on_progress(request, progress)
    
    def on_status_change(self, request: DownloadRequest, old_status: DownloadStatus, new_status: DownloadStatus) -> None:
        for observer in self.observers:
            observer.on_status_change(request, old_status, new_status)
    
    def on_error(self, request: DownloadRequest, error: Exception) -> None:
        for observer in self.observers:
            observer.on_error(request, error)
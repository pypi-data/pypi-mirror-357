import json
from enum import Enum, auto
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from typing import List, Dict, Any, Callable, Optional
import humanize

class DownloadStatus(Enum):
    FAILED = auto()
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    CANCELLED = auto()
    NOT_FOUND = auto()
    DUPLICATE = auto()
    PAUSED = auto()
    QUEUED = auto()

class ProtocolType(Enum):
    HTTP = auto()
    HTTPS = auto()
    FTP = auto()

RequestCallback = Callable[['DownloadRequest', int, int], None]

@dataclass_json
@dataclass
class DownloadRequest:
    name: str
    url: str
    status: DownloadStatus = field(
        default=DownloadStatus.PENDING,
        metadata=config(
            encoder=lambda s: s.value,
            decoder=lambda v: DownloadStatus(v)
        )
    )
    error_message: str = ""
    file_path: str = ""
    file_size: int = 0
    downloaded_size: int = 0
    progress: float = 0.0
    segments: int = 1
    priority: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    proxy: Optional[str] = None
    max_retries: int = 3
    timeout: float = 30.0
    speed_limit: Optional[int] = None
    resume_supported: bool = True

    retry_count: int = 0
    retry_delay: float = 1.0
    partial_file_path: Optional[str] = None
    checksum: Optional[str] = None
    checksum_type: str = "md5"

    ftp_username: Optional[str] = None
    ftp_password: Optional[str] = None
    ftp_passive: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__
    
    def to_json(self, **kwargs) -> str:
        return json.dumps(self.to_dict(), **kwargs)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadRequest':
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DownloadRequest':
        return cls.from_dict(json.loads(json_str))

@dataclass
class ProgressInfo:
    total_size: int
    downloaded_size: int
    speed: float
    eta: float
    elapsed_time: float
    progress_percent: float
    
    def __str__(self) -> str:
        return f"Progress: {self.progress_percent:.1f}% | Speed: {humanize.naturalsize(self.speed, binary=True)}/s | ETA: {self.eta:.0f}s"
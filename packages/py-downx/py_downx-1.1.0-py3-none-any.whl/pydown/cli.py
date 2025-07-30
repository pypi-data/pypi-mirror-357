#!/usr/bin/env python3
"""
PyDown CLI - Command Line Interface for the pydown library

A flexible command-line tool for downloading files with support for:
- Multiple protocols (HTTP/HTTPS, FTP, SFTP)
- Concurrent downloads
- Resume functionality
- Speed limiting
- Progress monitoring
- Batch downloads from file lists
"""

import argparse
import sys
import json
import os
import time
import signal
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse

from .manager import DownloadManager
from .models import DownloadRequest, DownloadStatus, ProgressInfo
from .utils import create_download_request
from .observers import DownloadObserver


class CLIProgressObserver(DownloadObserver):
    """Custom observer for CLI progress display"""
    
    def __init__(self, show_progress: bool = True, verbose: bool = False):
        self.show_progress = show_progress
        self.verbose = verbose
        self.last_update = {}
    
    def on_download_started(self, request: DownloadRequest):
        if self.verbose:
            print(f"📥 Started: {request.name} ({request.url})")
    
    def on_download_progress(self, request: DownloadRequest, progress_info: ProgressInfo):
        if not self.show_progress:
            return
            
        # Throttle updates to avoid spam
        current_time = time.time()
        if request.url in self.last_update:
            if current_time - self.last_update[request.url] < 0.5:
                return
        
        self.last_update[request.url] = current_time
        
        if progress_info.total_size > 0:
            progress = progress_info.progress_percent
            bar_length = 30
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            # Format sizes
            downloaded_mb = progress_info.downloaded_size / (1024 * 1024)
            total_mb = progress_info.total_size / (1024 * 1024)
            
            print(f"\r{request.name}: |{bar}| {progress:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='', flush=True)
    
    def on_download_completed(self, request: DownloadRequest):
        if self.show_progress:
            print()  # New line after progress bar
        print(f"✅ Completed: {request.name}")
        if self.verbose:
            print(f"   → Saved to: {request.file_path}")
    
    def on_download_failed(self, request: DownloadRequest, error: str):
        if self.show_progress:
            print()  # New line after progress bar
        print(f"❌ Failed: {request.name} - {error}")
    
    def on_download_paused(self, request: DownloadRequest):
        if self.show_progress:
            print()  # New line after progress bar
        print(f"⏸️  Paused: {request.name}")
    
    def on_progress(self, request: DownloadRequest, progress: ProgressInfo):
        """Implementation for DownloadObserver abstract method"""
        self.on_download_progress(request, progress)
    
    def on_status_change(self, request: DownloadRequest, old_status: DownloadStatus, new_status: DownloadStatus):
        """Implementation for DownloadObserver abstract method"""
        if new_status == DownloadStatus.COMPLETED:
            self.on_download_completed(request)
        elif new_status == DownloadStatus.FAILED:
            self.on_download_failed(request, request.error_message)
        elif new_status == DownloadStatus.PAUSED:
            self.on_download_paused(request)
        elif new_status == DownloadStatus.IN_PROGRESS:
            self.on_download_started(request)
    
    def on_error(self, request: DownloadRequest, error: Exception):
        """Implementation for DownloadObserver abstract method"""
        self.on_download_failed(request, str(error))


class PyDownCLI:
    """Main CLI application class"""
    
    def __init__(self):
        self.download_manager: Optional[DownloadManager] = None
        self.running = False
        
        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        print("\n🛑 Interrupt received. Stopping downloads...")
        self.running = False
        if self.download_manager:
            self.download_manager.stop()
        sys.exit(0)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser"""
        parser = argparse.ArgumentParser(
            prog='pydown',
            description='PyDown - Flexible file download manager',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Simple download
  pydown https://example.com/file.zip
  
  # Download with custom output path
  pydown https://example.com/file.zip -o /path/to/save/file.zip
  
  # Multiple downloads with options
  pydown url1 url2 url3 -c 5 -s 4 --speed-limit 1000000
  
  # Batch download from file
  pydown --batch urls.txt -d ./downloads/
  
  # Resume previous downloads
  pydown --resume session.json
  
  # SFTP download with credentials
  pydown sftp://user:pass@server/path/file.txt
            """)
        
        # Positional arguments
        parser.add_argument('urls', nargs='*', 
                          help='URLs to download (can be HTTP/HTTPS/FTP/SFTP)')
        
        # Output options
        output_group = parser.add_argument_group('Output Options')
        output_group.add_argument('-o', '--output', type=str,
                                help='Output file path (for single downloads)')
        output_group.add_argument('-d', '--directory', type=str, default='.',
                                help='Output directory (default: current directory)')
        
        # Download behavior
        download_group = parser.add_argument_group('Download Options')
        download_group.add_argument('-c', '--concurrent', type=int, default=3,
                                  help='Maximum concurrent downloads (default: 3)')
        download_group.add_argument('-s', '--segments', type=int, default=8,
                                  help='Maximum segments per download (default: 8)')
        download_group.add_argument('--speed-limit', type=int,
                                  help='Speed limit in bytes per second')
        download_group.add_argument('--timeout', type=float, default=30.0,
                                  help='Connection timeout in seconds (default: 30)')
        download_group.add_argument('--retries', type=int, default=3,
                                  help='Maximum retry attempts (default: 3)')
        download_group.add_argument('--duplicate', choices=['skip', 'overwrite', 'rename'],
                                  default='skip', help='Duplicate file handling strategy')
        
        # Authentication
        auth_group = parser.add_argument_group('Authentication')
        auth_group.add_argument('--username', type=str,
                              help='Username for FTP/SFTP')
        auth_group.add_argument('--password', type=str,
                              help='Password for FTP/SFTP')
        auth_group.add_argument('--headers', type=str,
                              help='HTTP headers as JSON string')
        auth_group.add_argument('--cookies', type=str,
                              help='HTTP cookies as JSON string')
        auth_group.add_argument('--proxy', type=str,
                              help='Proxy URL')
        
        # Batch operations
        batch_group = parser.add_argument_group('Batch Operations')
        batch_group.add_argument('--batch', type=str,
                               help='File containing URLs to download (one per line)')
        batch_group.add_argument('--save-session', type=str,
                               help='Save download session to JSON file')
        batch_group.add_argument('--resume', type=str,
                               help='Resume downloads from saved session file')
        
        # Display options
        display_group = parser.add_argument_group('Display Options')
        display_group.add_argument('-q', '--quiet', action='store_true',
                                 help='Suppress progress output')
        display_group.add_argument('-v', '--verbose', action='store_true',
                                 help='Verbose output')
        display_group.add_argument('--no-progress', action='store_true',
                                 help='Disable progress bars')
        display_group.add_argument('--log-file', type=str,
                                 help='Log to file')
        
        # Special commands
        parser.add_argument('--version', action='version', version='PyDown 1.0.0')
        
        return parser
    
    def parse_json_arg(self, json_str: str, arg_name: str) -> Dict:
        """Parse JSON argument safely"""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing {arg_name}: {e}")
            sys.exit(1)
    
    def load_urls_from_file(self, file_path: str) -> List[str]:
        """Load URLs from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = []
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Support format: URL [output_path]
                        parts = line.split(None, 1)
                        urls.append(parts[0])
                return urls
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file '{file_path}': {e}")
            sys.exit(1)
    
    def save_session(self, file_path: str, downloads: Dict[str, DownloadRequest]):
        """Save download session to JSON file"""
        try:
            session_data = {
                'downloads': [req.to_dict() for req in downloads.values()],
                'timestamp': time.time()
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
            print(f"💾 Session saved to {file_path}")
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def load_session(self, file_path: str) -> List[DownloadRequest]:
        """Load download session from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            downloads = []
            for req_data in session_data.get('downloads', []):
                try:
                    req = DownloadRequest.from_dict(req_data)
                    # Reset status for incomplete downloads
                    if req.status in [DownloadStatus.IN_PROGRESS, DownloadStatus.FAILED]:
                        req.status = DownloadStatus.PENDING
                    downloads.append(req)
                except Exception as e:
                    print(f"Warning: Could not restore download {req_data.get('url', 'unknown')}: {e}")
            
            print(f"📂 Loaded {len(downloads)} downloads from session")
            return downloads
            
        except FileNotFoundError:
            print(f"Error: Session file '{file_path}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading session: {e}")
            sys.exit(1)
    
    def create_download_request_from_args(self, url: str, args: argparse.Namespace, 
                                        index: int = 0) -> DownloadRequest:
        """Create a download request from CLI arguments"""
        # Determine output path
        if args.output and len(args.urls) == 1:
            output_path = args.output
        else:
            # Auto-generate filename from URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or f"download_{index}"
            output_path = os.path.join(args.directory, filename)
        
        # Parse optional JSON arguments
        headers = self.parse_json_arg(args.headers, 'headers') if args.headers else {}
        cookies = self.parse_json_arg(args.cookies, 'cookies') if args.cookies else {}
        
        # Create request
        request = create_download_request(
            name=os.path.basename(output_path),
            url=url,
            file_path=output_path,
            segments=args.segments,
            headers=headers,
            cookies=cookies,
            proxy=args.proxy,
            max_retries=args.retries,
            timeout=args.timeout,
            speed_limit=args.speed_limit
        )
        
        return request
    def run(self, args: Optional[List[str]] = None) -> int:
        """Main entry point for the CLI"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Validate arguments
        if not parsed_args.urls and not parsed_args.batch and not parsed_args.resume:
            parser.print_help()
            return 1
        
        # Create output directory if needed
        if parsed_args.directory != '.':
            os.makedirs(parsed_args.directory, exist_ok=True)
        
        # Initialize download manager
        self.download_manager = DownloadManager(
            max_concurrent_downloads=parsed_args.concurrent,
            max_segments_per_download=parsed_args.segments,
            duplicate_strategy=parsed_args.duplicate,
            log_file=parsed_args.log_file,
            quiet=parsed_args.quiet
        )
        
        # Add CLI progress observer
        if not parsed_args.quiet:
            cli_observer = CLIProgressObserver(
                show_progress=not parsed_args.no_progress,
                verbose=parsed_args.verbose
            )
            self.download_manager.add_observer(cli_observer)
        
        downloads = []
        
        # Handle resume session
        if parsed_args.resume:
            downloads.extend(self.load_session(parsed_args.resume))
        
        # Handle batch file
        if parsed_args.batch:
            batch_urls = self.load_urls_from_file(parsed_args.batch)
            for i, url in enumerate(batch_urls):
                request = self.create_download_request_from_args(url, parsed_args, i)
                downloads.append(request)
        
        # Handle individual URLs
        if parsed_args.urls:
            for i, url in enumerate(parsed_args.urls):
                request = self.create_download_request_from_args(url, parsed_args, i)
                downloads.append(request)
        
        if not downloads:
            print("No downloads to process")
            return 1
        
        # Add downloads to manager
        print(f"🚀 Adding {len(downloads)} downloads...")
        for request in downloads:
            self.download_manager.add_download(request)
            if parsed_args.verbose:
                print(f"   Added: {request.name} → {request.file_path}")
        
        # Start downloads
        print("⏬ Starting downloads...")
        self.running = True
        self.download_manager.start()
        
        try:
            # Wait for completion
            self.download_manager.wait_for_completion()
        except KeyboardInterrupt:
            print("\n🛑 Downloads interrupted by user")
        finally:
            self.download_manager.stop()
            self.running = False
        
        # Save session if requested
        if parsed_args.save_session:
            self.save_session(parsed_args.save_session, self.download_manager.downloads)
        
        # Print summary
        completed = sum(1 for req in self.download_manager.downloads.values() 
                       if req.status == DownloadStatus.COMPLETED)
        failed = sum(1 for req in self.download_manager.downloads.values() 
                    if req.status == DownloadStatus.FAILED)
        
        print(f"\n📊 Summary: {completed} completed, {failed} failed out of {len(downloads)} total")
        
        return 0 if failed == 0 else 1


def main():
    """Entry point for the pydown command"""
    cli = PyDownCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())

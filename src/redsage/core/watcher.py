import os
import time
from typing import List, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class FileChange:
    """
    Dataclass representing a file system change event.
    """
    path: str
    type: str  # 'created', 'modified', 'deleted'
    timestamp: float = time.time()

class RedSageFileHandler(FileSystemEventHandler):
    """
    Custom file system event handler for tracking file changes.
    """
    def __init__(self, ignore_patterns: List[str] = None):
        """
        Initialize file handler with optional ignore patterns.
        
        :param ignore_patterns: List of glob patterns to ignore
        """
        self.changes: List[FileChange] = []
        self.ignore_patterns = ignore_patterns or []

    def _should_ignore(self, path: str) -> bool:
        """
        Check if a file should be ignored based on patterns.
        
        :param path: File path to check
        :return: Boolean indicating if file should be ignored
        """
        return any(
            Path(path).match(pattern) 
            for pattern in self.ignore_patterns
        )

    def on_created(self, event):
        """
        Handle file creation events.
        
        :param event: Watchdog file system event
        """
        if not event.is_directory and not self._should_ignore(event.src_path):
            self.changes.append(FileChange(
                path=event.src_path, 
                type='created'
            ))

    def on_modified(self, event):
        """
        Handle file modification events.
        
        :param event: Watchdog file system event
        """
        if not event.is_directory and not self._should_ignore(event.src_path):
            self.changes.append(FileChange(
                path=event.src_path, 
                type='modified'
            ))

    def on_deleted(self, event):
        """
        Handle file deletion events.
        
        :param event: Watchdog file system event
        """
        if not event.is_directory and not self._should_ignore(event.src_path):
            self.changes.append(FileChange(
                path=event.src_path, 
                type='deleted'
            ))

class FileWatcher:
    """
    Main file watching system for monitoring file system changes.
    """
    def __init__(
        self, 
        paths: List[str], 
        ignore_patterns: List[str] = None
    ):
        """
        Initialize file watcher for specified paths.
        
        :param paths: List of directories to watch
        :param ignore_patterns: Optional list of patterns to ignore
        """
        self.paths = [os.path.abspath(path) for path in paths]
        self.ignore_patterns = ignore_patterns or ['*.pyc', '__pycache__']
        
        # Initialize observer and event handler
        self.observer = Observer()
        self.handler = RedSageFileHandler(self.ignore_patterns)
        
        # Configure watching for each path
        for path in self.paths:
            self.observer.schedule(
                self.handler, 
                path, 
                recursive=True
            )

    def start_watching(self):
        """
        Start the file system monitoring process.
        """
        self.observer.start()

    def stop_watching(self):
        """
        Stop the file system monitoring process.
        """
        self.observer.stop()
        self.observer.join()

    def get_changes(self, clear: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve tracked file changes.
        
        :param clear: Whether to clear changes after retrieval
        :return: List of file changes as dictionaries
        """
        changes = [asdict(change) for change in self.handler.changes]
        
        if clear:
            self.handler.changes.clear()
        
        return changes

    def __enter__(self):
        """
        Context manager entry point for starting watcher. 
        """
        self.start_watching()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point for stopping watcher.
        """
        self.stop_watching()
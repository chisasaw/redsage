import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta

@dataclass
class ContextEntry:
    """
    Represents a single context entry with metadata and content. 
    """
    content: str
    type: str  # 'code', 'suggestion', 'explanation'
    timestamp: datetime = field(default_factory=datetime.now)
    file_path: Optional[str] = None
    language: Optional[str] = None
    tokens: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context entry to a dictionary representation.
        
        :return: Dictionary representation of the entry
        """
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

class ContextManager:
    """
    Manages conversation and code context for RedSage pair programming assistant.
    """
    def __init__(
        self, 
        max_entries: int = 50, 
        max_age_days: int = 7, 
        cache_dir: Optional[str] = None
    ):
        """
        Initialize context manager with configurable parameters.
        
        :param max_entries: Maximum number of context entries to maintain
        :param max_age_days: Maximum age of entries in days
        :param cache_dir: Optional directory for persistent context storage
        """
        self.max_entries = max_entries
        self.max_age_days = max_age_days
        
        # Determine cache directory
        self.cache_dir = cache_dir or os.path.join(
            os.path.expanduser('~'), 
            '.redsage', 
            'context_cache'
        )
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Context storage
        self.entries: List[ContextEntry] = []
    
    def add_entry(
        self, 
        content: str, 
        type: str, 
        file_path: Optional[str] = None, 
        language: Optional[str] = None
    ) -> ContextEntry:
        """
        Add a new context entry to the manager.
        
        :param content: Content of the entry
        :param type: Type of context entry
        :param file_path: Optional associated file path
        :param language: Optional programming language
        :return: Created context entry
        """
        # Estimate tokens (simple approximation)
        tokens = len(content) // 4
        
        # Create context entry
        entry = ContextEntry(
            content=content,
            type=type,
            file_path=file_path,
            language=language,
            tokens=tokens
        )
        
        # Add to entries
        self.entries.append(entry)
        
        # Prune old or excess entries
        self._prune_entries()
        
        return entry
    
    def _prune_entries(self):
        """
        Remove old or excess context entries based on configured limits.
        """
        current_time = datetime.now()
        
        # Filter out entries older than max_age_days
        self.entries = [
            entry for entry in self.entries
            if (current_time - entry.timestamp) < timedelta(days=self.max_age_days)
        ]
        
        # Truncate to max_entries
        self.entries = self.entries[-self.max_entries:]
    
    def get_context(
        self, 
        max_tokens: int = 4000, 
        types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve context entries, optionally filtered by type and token limit.
        
        :param max_tokens: Maximum total tokens to return
        :param types: Optional list of entry types to include
        :return: List of context entries
        """
        # Filter by types if specified
        filtered_entries = self.entries if types is None else [
            entry for entry in self.entries if entry.type in types
        ]
        
        # Sort entries and track token count
        context_window = []
        total_tokens = 0
        
        for entry in reversed(filtered_entries):
            if total_tokens + entry.tokens <= max_tokens:
                context_window.insert(0, entry.to_dict())
                total_tokens += entry.tokens
            else:
                break
        
        return context_window
    
    def save_context(self, filename: Optional[str] = None):
        """
        Save current context to a JSON file.
        
        :param filename: Optional custom filename
        """
        if not filename:
            filename = f"context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.cache_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(
                [entry.to_dict() for entry in self.entries], 
                f, 
                indent=2
            )
    
    def load_context(self, filename: str):
        """
        Load context from a JSON file.
        
        :param filename: Filename to load from cache directory
        """
        filepath = os.path.join(self.cache_dir, filename)
        
        with open(filepath, 'r') as f:
            loaded_entries = json.load(f)
            
        self.entries = [
            ContextEntry(
                content=entry['content'],
                type=entry['type'],
                timestamp=datetime.fromisoformat(entry['timestamp']),
                file_path=entry.get('file_path'),
                language=entry.get('language'),
                tokens=entry.get('tokens', 0)
            ) for entry in loaded_entries
        ]
    
    def clear_context(self):
        """
        Clear all context entries.
        """
        self.entries.clear()
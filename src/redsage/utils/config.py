import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    """ 
    Configuration management for RedSage pair programming assistant.
    Handles loading, validating, and accessing configuration settings.
    """
    DEFAULT_CONFIG = {
        'llm': {
            'provider': 'openai',
            'model': 'gpt-4o',
            'max_tokens': 4000
        },
        'watch': {
            'paths': ['./src'],
            'ignore': ['*.pyc', '__pycache__', '.git']
        },
        'git': {
            'enabled': True,
            'branch_prefix': 'redsage/'
        },
        'context': {
            'max_entries': 50,
            'max_age_days': 7
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration with optional custom path.
        
        :param config_path: Path to custom configuration file
        """
        # Determine configuration file location
        self.config_path = self._resolve_config_path(config_path)
        
        # Load configuration
        self.config = self._load_config()
    
    def _resolve_config_path(self, config_path: Optional[str] = None) -> Path:
        """
        Resolve the configuration file path.
        
        :param config_path: Optional user-specified path
        :return: Resolved configuration file path
        """
        # User-specified path takes precedence
        if config_path:
            return Path(config_path)
        
        # Default configuration locations
        config_locations = [
            Path.cwd() / 'redsage.yml',
            Path.cwd() / 'redsage.yaml',
            Path.home() / '.config' / 'redsage' / 'config.yml',
            Path.home() / '.redsage.yml'
        ]
        
        # Find first existing configuration
        for location in config_locations:
            if location.exists():
                return location
        
        # Create default configuration if none exists
        default_config_path = Path.home() / '.config' / 'redsage' / 'config.yml'
        default_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        return default_config_path
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default.
        
        :return: Loaded or default configuration dictionary
        """
        try:
            # Try to load existing configuration
            if self.config_path.exists():
                with open(self.config_path, 'r') as config_file:
                    user_config = yaml.safe_load(config_file) or {}
                
                # Deep merge with default configuration
                return self._deep_merge(self.DEFAULT_CONFIG, user_config)
            
            # Create default configuration file
            default_config = self.DEFAULT_CONFIG.copy()
            with open(self.config_path, 'w') as config_file:
                yaml.dump(default_config, config_file, default_flow_style=False)
            
            return default_config
        
        except Exception as e:
            # Fallback to default configuration
            print(f"Error loading config: {e}. Using default configuration.")
            return self.DEFAULT_CONFIG
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries.
        
        :param base: Base configuration dictionary
        :param update: Update configuration dictionary
        :return: Merged configuration dictionary
        """
        merged = base.copy()
        for key, value in update.items():
            if isinstance(value, dict):
                merged[key] = self._deep_merge(merged.get(key, {}), value)
            else:
                merged[key] = value
        return merged
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve configuration value with optional default.
        
        :param key: Configuration key (supports dot notation)
        :param default: Default value if key not found
        :return: Configuration value
        """
        # Support dot notation for nested keys
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value if value is not None else default
    
    def update(self, updates: Dict[str, Any]):
        """
        Update configuration with new values.
        
        :param updates: Dictionary of configuration updates
        """
        self.config = self._deep_merge(self.config, updates)
        
        # Persist updates to configuration file
        try:
            with open(self.config_path, 'w') as config_file:
                yaml.dump(self.config, config_file, default_flow_style=False)
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def validate(self) -> bool:
        """
        Validate configuration settings.
        
        :return: Whether configuration is valid
        """
        # Check required configuration sections
        required_sections = ['llm', 'watch', 'git']
        for section in required_sections:
            if section not in self.config:
                return False
        
        # Validate specific settings
        if not isinstance(self.get('watch.paths'), list):
            return False
        
        if not self.get('llm.provider') in ['claude', 'openai']:
            return False
        
        return True
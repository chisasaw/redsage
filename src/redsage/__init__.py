# RedSage: Minimal Terminal Pair Programmer
# Package initialization and version management 

# Version information
__version__ = "0.1.0"
__author__ = "RedSage Team"
__email__ = "warrenchisasa@gmail"

# Core package imports for easy access 
from redsage.cli import RedSageCLI, main
from redsage.core.agent import RedSageAgent
from redsage.core.watcher import FileWatcher
from redsage.llm.base import BaseLLMProvider
from redsage.utils.config import Config
from redsage.utils.git import GitManager 

# Package-level configuration 
__all__ = [
    'RedSageCLI',
    'main',
    'RedSageAgent',
    'FileWatcher',
    'BaseLLMProvider',
    'Config',
    'GitManager'
]

# Package-level docstring
__doc__ = """
RedSage: A lightweight terminal-based pair programming assistant.

Features:
- Multi-LLM support (Claude, OpenAI)
- Real-time file watching
- Git integration
- Simple command-line interface
"""
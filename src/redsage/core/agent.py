import os
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod 

from redsage.llm.base import BaseLLMProvider
from redsage.llm.openai import OpenAILLMProvider 
from redsage.utils.config import Config
from redsage.utils.git import GitManager

class RedSageAgent:
    """
    Central agent for managing LLM interactions and code suggestions 
    in the RedSage terminal pair programming environment.
    """
    def __init__(self, config: Config):
        """
        Initialize the RedSage agent with configuration and LLM provider.
        
        :param config: Configuration object with LLM and system settings
        """
        self.config = config
        self.llm_provider = self._initialize_llm_provider(config.get('llm', {}).get('provider', 'openai'))
        self.git_manager = GitManager(config)
        
        # Conversation context tracking
        self.context: Dict[str, Any] = {
            'files': [],
            'recent_changes': [],
            'conversation_history': []
        }
    
    def _initialize_llm_provider(self, provider: str) -> BaseLLMProvider:
        """
        Initialize the appropriate LLM provider based on configuration.
        
        :param provider: Name of the LLM provider (e.g., 'openai') 
        :return: Initialized LLM provider instance
        """
        providers = {
            'openai': OpenAILLMProvider
        }
        provider_class = providers.get(provider.lower())
        if not provider_class:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        api_key = os.getenv('REDSAGE_API_KEY')
        if api_key:
            return provider_class(api_key=api_key)
        else:
            raise ValueError("REDSAGE_API_KEY environment variable is not set.")
   
    def update_context(self, files: List[str], changes: Optional[List[Dict[str, Any]]] = None):
        """
        Update the current conversation context with file and change information.
        
        :param files: List of files being tracked
        :param changes: Optional list of file changes
        """
        self.context['files'] = list(set(self.context['files'] + files))
        
        if changes:
            self.context['recent_changes'].extend(changes)
            # Limit recent changes to last 10 entries
            self.context['recent_changes'] = self.context['recent_changes'][-10:]
    
    def process_command(self, command: str) -> str:
        """
        Process user commands and route to appropriate actions.
        
        :param command: User-entered command
        :return: Command execution result
        """
        # Command routing based on user input
        command_handlers = {
            '/context': self._show_context,
            '/suggest': self._get_suggestions,
            '/explain': self._explain_code,
            '/diff': self._show_changes,
            '/save': self._save_changes,
            '/undo': self._undo_last_change,
            '/switch': self._switch_provider
        }
        
        # Split command to handle variations
        cmd_parts = command.split(maxsplit=1)
        base_cmd = cmd_parts[0]
        
        handler = command_handlers.get(base_cmd)
        if handler:
            return handler(cmd_parts[1] if len(cmd_parts) > 1 else None)
        
        return self._default_suggestion(command)
    
    def get_suggestion(self, query: str) -> str:
        """
        Generate a code suggestion based on current context and user query.
        
        :param query: User's natural language query or code request
        :return: LLM-generated suggestion
        """
        # Prepare context for LLM
        context_str = self._prepare_context_prompt()
        
        # Generate response from LLM
        try:
            suggestion = self.llm_provider.generate_response(
                prompt=query,
                context=context_str
            )
            
            # Track conversation history
            self.context['conversation_history'].append({
                'query': query,
                'suggestion': suggestion
            })
            
            return suggestion
        except Exception as e:
            return f"Error generating suggestion: {str(e)}"
    
    def _prepare_context_prompt(self) -> str:
        """
        Compile context information for LLM prompt generation.
        
        :return: Formatted context string
        """
        context_parts = []
        
        # Add tracked files
        if self.context['files']:
            context_parts.append(f"Tracked Files: {', '.join(self.context['files'])}")
        
        # Add recent changes
        if self.context['recent_changes']:
            changes_summary = ', '.join([
                f"{change.get('file', 'Unknown')} ({change.get('type', 'modified')})" 
                for change in self.context['recent_changes']
            ])
            context_parts.append(f"Recent Changes: {changes_summary}")
        
        return '\n'.join(context_parts)
    
    def _show_context(self, _: Optional[str] = None) -> str:
        """Display current conversation context."""
        return str(self.context)
    
    def _get_suggestions(self, query: Optional[str] = None) -> str:
        """Get code suggestions based on optional query."""
        return self.get_suggestion(query or "Provide code improvement suggestions")
    
    def _explain_code(self, code: Optional[str] = None) -> str:
        """Explain the provided code or last context."""
        explanation_query = f"Explain the following code: {code}" if code else "Explain recent code context"
        return self.get_suggestion(explanation_query)
    
    def _show_changes(self, _: Optional[str] = None) -> str:
        """Show recent file changes."""
        return str(self.context['recent_changes'])
    
    def _save_changes(self, branch_name: Optional[str] = None) -> str:
        """Save current changes to a git branch."""
        return self.git_manager.save_changes(branch_name)
    
    def _undo_last_change(self, _: Optional[str] = None) -> str:
        """Undo the most recent change."""
        return self.git_manager.undo_last_change()
    
    def _switch_provider(self, new_provider: Optional[str] = None) -> str:
        """Switch the current LLM provider."""
        if not new_provider:
            return "OpenAI is the only supported provider."
        
        try:
            self.llm_provider = self._initialize_llm_provider(new_provider)
            return f"Switched to {new_provider} provider"
        except ValueError as e:
            return str(e)
    
    def _default_suggestion(self, query: str) -> str:
        """Fallback method for unrecognized commands.""" 
        return self.get_suggestion(query)

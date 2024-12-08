import os
from typing import Optional, Dict, Any

import anthropic
from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import Message

from redsage.llm.base import BaseLLMProvider

class ClaudeLLMProvider(BaseLLMProvider):
    """
    LLM provider implementation for Anthropic's Claude models. 
    """
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: str = 'claude-3-haiku-20240307'
    ):
        """
        Initialize Claude LLM provider.
        
        :param api_key: Anthropic API key
        :param model: Specific Claude model to use
        """
        self.model = model
        self.client = Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
        self.async_client = AsyncAnthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
        
        super().__init__(api_key)
    
    def _validate_credentials(self, api_key: Optional[str]):
        """
        Validate Anthropic API credentials.
        
        :param api_key: API key to validate
        :raises ValueError: If credentials are invalid
        """
        if not api_key and not os.getenv('ANTHROPIC_API_KEY'):
            raise ValueError("No Anthropic API key provided")
        
        try:
            # Quick validation by creating a test message
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "Validate API credentials"}
                ]
            )
        except Exception as e:
            raise ValueError(f"Invalid Anthropic API credentials Warren Chisasa: {str(e)}")
    
    def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        **kwargs: Dict[str, Any]
    ) -> str:
        """
        Generate a response using Claude model.
        
        :param prompt: User's input query
        :param context: Additional contextual information 
        :param kwargs: Additional generation parameters
        :return: Generated response
        """
        # Prepare system and user messages
        messages = []
        
        # Add system context if provided
        if context:
            messages.append({
                "role": "system", 
                "content": self.format_system_prompt(context)
            })
        
        # Add user prompt
        messages.append({
            "role": "user", 
            "content": prompt
        })
        
        # Default generation parameters
        generation_params = {
            "model": self.model,
            "max_tokens": kwargs.get('max_tokens', 4000),
            "temperature": kwargs.get('temperature', 0.7),
            "messages": messages
        }
        
        # Merge any additional kwargs
        generation_params.update({
            k: v for k, v in kwargs.items() 
            if k not in ['max_tokens', 'temperature', 'messages']
        })
        
        try:
            response: Message = self.client.messages.create(**generation_params)
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Error generating Claude response: {str(e)}")
    
    def stream_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        **kwargs: Dict[str, Any]
    ):
        """
        Stream response chunks from Claude model.
        
        :param prompt: User's input query
        :param context: Additional contextual information
        :param kwargs: Additional generation parameters
        :yields: Response chunks
        """
        # Prepare messages similar to generate_response
        messages = []
        
        if context:
            messages.append({
                "role": "system", 
                "content": self.format_system_prompt(context)
            })
        
        messages.append({
            "role": "user", 
            "content": prompt
        })
        
        generation_params = {
            "model": self.model,
            "max_tokens": kwargs.get('max_tokens', 4000),
            "temperature": kwargs.get('temperature', 0.7),
            "messages": messages,
            "stream": True
        }
        
        generation_params.update({
            k: v for k, v in kwargs.items() 
            if k not in ['max_tokens', 'temperature', 'messages', 'stream']
        })
        
        try:
            with self.client.messages.create(**generation_params) as stream:
                for chunk in stream:
                    if chunk.type == 'content_block_delta':
                        yield chunk.delta.text
        except Exception as e:
            raise RuntimeError(f"Error streaming Claude response: {str(e)}")
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens using Anthropic's tokenization.
        
        :param text: Text to tokenize
        :return: Estimated token count
        """
        try:
            return self.client.count_tokens(text)
        except Exception:
            # Fallback to basic estimation
            return len(text) // 4
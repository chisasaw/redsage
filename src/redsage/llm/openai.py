import os
from typing import Optional, Dict, Any, Iterator

import openai
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from redsage.llm.base import BaseLLMProvider

class OpenAILLMProvider(BaseLLMProvider):
    """
    LLM provider implementation for OpenAI's language models. 
    """
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: str = 'gpt-3.5-turbo'
    ):
        """
        Initialize OpenAI LLM provider.
        
        :param api_key: OpenAI API key
        :param model: Specific OpenAI model to use
        """
        self.model = model
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.async_client = AsyncOpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        
        super().__init__(api_key)
    
    def _validate_credentials(self, api_key: Optional[str]):
        """
        Validate OpenAI API credentials.
        
        :param api_key: API key to validate
        :raises ValueError: If credentials are invalid
        """
        if not api_key and not os.getenv('OPENAI_API_KEY'):
            raise ValueError("No OpenAI API key provided")
        
        try:
            # Quick validation by creating a test chat completion
            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Validate API credentials"}
                ],
                max_tokens=10
            )
        except Exception as e:
            raise ValueError(f"Invalid OpenAI API credentials: {str(e)}")
    
    def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        **kwargs: Dict[str, Any]
    ) -> str:
        """
        Generate a response using OpenAI model.
        
        :param prompt: User's input query
        :param context: Additional contextual information
        :param kwargs: Additional generation parameters
        :return: Generated response
        """
        # Prepare messages for chat completion
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
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', 4000),
            "temperature": kwargs.get('temperature', 0.7)
        }
        
        # Merge any additional kwargs
        generation_params.update({
            k: v for k, v in kwargs.items() 
            if k not in ['max_tokens', 'temperature', 'messages']
        })
        
        try:
            response: ChatCompletion = self.client.chat.completions.create(**generation_params)
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"Error generating OpenAI response: {str(e)}")
    
    def stream_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        **kwargs: Dict[str, Any]
    ) -> Iterator[str]:
        """
        Stream response chunks from OpenAI model.
        
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
        
        # Default generation parameters
        generation_params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', 4000),
            "temperature": kwargs.get('temperature', 0.7),
            "stream": True
        }
        
        # Merge any additional kwargs
        generation_params.update({
            k: v for k, v in kwargs.items() 
            if k not in ['max_tokens', 'temperature', 'messages', 'stream']
        })
        
        try:
            stream: Iterator[ChatCompletionChunk] = self.client.chat.completions.create(**generation_params)
            
            for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
        except Exception as e:
            raise RuntimeError(f"Error streaming OpenAI response: {str(e)}")
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens using OpenAI's tiktoken library.
        
        :param text: Text to tokenize
        :return: Estimated token count
        """
        try:
            # Import tiktoken dynamically to avoid mandatory dependency 
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except ImportError:
            # Fallback to basic estimation if tiktoken not available
            return len(text) // 4
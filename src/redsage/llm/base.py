from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseLLMProvider(ABC):
    """
    Abstract base class defining the interface for Language Model providers
    in the RedSage pair programming assistant.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM provider with optional API key.
        
        :param api_key: API key for authentication
        """
        self._validate_credentials(api_key)
    
    @abstractmethod
    def _validate_credentials(self, api_key: Optional[str]):
        """
        Validate the provided API credentials.
        
        Implementations should:
        - Check API key format
        - Verify connectivity with the LLM service
        - Raise ValueError for invalid credentials
        
        :param api_key: API key to validate
        :raises ValueError: If credentials are invalid
        """
        pass
    
    @abstractmethod
    def generate_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        **kwargs: Dict[str, Any]
    ) -> str:
        """
        Generate a response from the Language Model.
        
        :param prompt: User's input query or request
        :param context: Additional contextual information
        :param kwargs: Additional generation parameters
        :return: Generated response from the LLM
        """
        pass
    
    def stream_response(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        **kwargs: Dict[str, Any]
    ):
        """
        Optional method for streaming responses.
        
        :param prompt: User's input query or request
        :param context: Additional contextual information
        :param kwargs: Additional generation parameters
        :yields: Streamed response chunks
        """
        # Default implementation falls back to generate_response
        yield self.generate_response(prompt, context, **kwargs)
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in the given text.
        
        :param text: Input text to tokenize
        :return: Estimated token count
        """
        # Basic token estimation (1 token ≈ 4 characters)
        return len(text) // 4
    
    def truncate_to_token_limit(
        self, 
        text: str, 
        max_tokens: int = 4000
    ) -> str:
        """
        Truncate text to fit within token limits.
        
        :param text: Input text to potentially truncate
        :param max_tokens: Maximum allowed tokens
        :return: Truncated text
        """
        # Simple token-based truncation
        while self.estimate_tokens(text) > max_tokens:
            # Remove from the end of the text
            text = text[:-(len(text) // 10)]
        return text
    
    def format_system_prompt(self, context: Optional[str] = None) -> str:
        """
        Format a system-level prompt with optional context.
        
        :param context: Contextual information to include
        :return: Formatted system prompt 
        """
        base_prompt = (
    "You are a highly skilled pair programming assistant designed for terminal use. "
    "Your role is to collaborate with a developer by providing clear, concise, and accurate code suggestions, "
    "along with detailed but succinct explanations tailored to the context. "
    "When offering code snippets, ensure they are optimized, follow best practices, and are compatible with the described environment. "
    "Explain alternative approaches or potential improvements when relevant. "
    "Prioritize clarity and maintain a conversational tone. "
    "If asked to debug, analyze the problem efficiently and propose actionable solutions with explanations."
)

        
        if context:
            base_prompt += f"\n\nCurrent Context:\n{context}"
        
        return base_prompt
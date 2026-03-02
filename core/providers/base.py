from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseProvider(ABC):
    """Abstract base class for AI providers (Ollama, Gemini, Claude, etc.)"""
    
    @abstractmethod
    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Standard completion interface."""
        pass

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat completion interface."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of the provider."""
        pass

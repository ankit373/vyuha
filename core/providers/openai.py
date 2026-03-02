import httpx
import os
from typing import List, Dict, Any, Optional
from core.providers.base import BaseProvider
from core.logger import logger

class OpenAIProvider(BaseProvider):
    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1"):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url

    def name(self) -> str:
        return f"OpenAI({self.model})"

    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages)

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                return data['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"OpenAI chat failed: {e}")
                raise

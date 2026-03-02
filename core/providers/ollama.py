import httpx
import json
from typing import List, Dict, Any, Optional
from core.providers.base import BaseProvider
from core.logger import logger

class OllamaProvider(BaseProvider):
    def __init__(self, model: str = "llama3.2:1b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.timeout = 300.0

    def name(self) -> str:
        return f"Ollama({self.model})"

    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        logger.info(f"Ollama Prompt: {prompt[:100]}...")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                res_text = response.json().get("response", "")
                logger.info(f"Ollama Response: {res_text[:100]}...")
                return res_text
            except Exception as e:
                logger.error(f"Ollama completion failed: {e}")
                raise

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                return response.json().get("message", {}).get("content", "")
            except Exception as e:
                logger.error(f"Ollama chat failed: {e}")
                raise

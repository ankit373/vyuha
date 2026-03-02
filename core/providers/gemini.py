import httpx
import os
from typing import List, Dict, Any, Optional
from core.providers.base import BaseProvider
from core.logger import logger

class GeminiProvider(BaseProvider):
    def __init__(self, model: str = "gemini-1.5-flash", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def name(self) -> str:
        return f"Gemini({self.model})"

    async def complete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Instruction: {system_prompt}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        
        payload = {"contents": contents}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                logger.error(f"Gemini completion failed: {e}")
                raise

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        # Simplified Gemini chat mapping
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        contents = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
        payload = {"contents": contents}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                logger.error(f"Gemini chat failed: {e}")
                raise

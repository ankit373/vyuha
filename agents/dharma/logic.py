from core.agent_base import BaseAgent
from core.bus import Message, bus
from typing import List
from core.logger import logger

class Dharma(BaseAgent):
    def get_topics(self) -> List[str]:
        return []

    async def handle_message(self, message: Message):
        pass

from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger

class Lipi(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["docs/input"]

    async def handle_message(self, message: Message):
        if message.topic == "docs/input":
            logger.info(f"Lipi: Drafting documentation for the project...")
            
            docs_prompt = (
                "Act as a Senior Technical Scribe. Generate world-class project documentation for: {message.payload}. "
                "Include a comprehensive README.md, exhaustive API references, and developer boarding guides with high technical clarity."
            )
            docs = await self.ask_ai(docs_prompt)
            
            # Submit for review by Sutradhara
            await self.send_message(
                topic="docs/draft",
                payload={"docs": docs},
                is_action=True,
                trace_id=message.trace_id
            )

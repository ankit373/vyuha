from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger

class Akasha(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["connectivity/input", "connectivity/verified"]

    async def handle_message(self, message: Message):
        if message.topic == "connectivity/input":
            logger.info(f"Akasha: Designing connectivity and API integration plan...")
            
            prompt = (
                "Act as a Lead Connectivity Architect. Design a production-grade API topology, inter-service communication protocols, "
                f"and resilient data flow for: {message.payload}. Focus on reliability, latency, and scalability. Output a high-fidelity connectivity blueprint."
            )
            conn_plan = await self.ask_ai(prompt)
            
            # Submit for review by Vishwakarma
            await self.send_message(
                topic="connectivity/draft",
                payload={"conn_plan": conn_plan},
                is_action=True,
                trace_id=message.trace_id
            )

        elif message.topic == "connectivity/verified":
            logger.info(f"Akasha: Connectivity plan verified and ready.")
            # Notify architecture that integration is ready
            await self.send_message(
                topic="architecture/integration_ready",
                payload=message.payload,
                trace_id=message.trace_id
            )

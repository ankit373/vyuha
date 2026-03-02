from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger

class Prithvi(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["infrastructure/input", "infrastructure/verified"]

    async def handle_message(self, message: Message):
        if message.topic == "infrastructure/input":
            logger.info(f"Prithvi: Provisioning infrastructure and IaC scripts...")
            
            prompt = (
                "Act as a Lead Infrastructure Architect. Design and generate high-fidelity Terraform or Cloud Config scripts for: {message.payload}. "
                "Ensure production-grade scalability, resilient networking, and strict security compliance."
            )
            infra_plan = await self.ask_ai(prompt)
            
            # Submit for review by Kavacha and Arjuna
            await self.send_message(
                topic="infrastructure/draft",
                payload={"infra_plan": infra_plan},
                is_action=True,
                trace_id=message.trace_id
            )

        elif message.topic == "infrastructure/verified":
            logger.info(f"Prithvi: Infrastructure verified and provisioned.")
            # Ready for deployment

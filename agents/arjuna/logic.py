from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger

class Arjuna(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["deployment/input", "deployment/verified"]

    async def handle_message(self, message: Message):
        if message.topic == "deployment/input":
            logger.info(f"Arjuna: Creating deployment pipeline and release plan...")
            
            prompt = (
                "Act as a Lead DevOps Engineer. Architect a production-grade CI/CD pipeline and automated release strategy for: {message.payload}. "
                "Focus on zero-downtime deployments, health checkpoints, and resilient rollback logic."
            )
            deploy_plan = await self.ask_ai(prompt)
            
            # Submit for review by Kavacha and Prithvi
            await self.send_message(
                topic="deployment/draft",
                payload={"deploy_plan": deploy_plan},
                is_action=True,
                trace_id=message.trace_id
            )

        elif message.topic == "deployment/verified":
            logger.info(f"Arjuna: Deployment plan verified. Executing release...")
            # Trigger final status
            await self.send_message(topic="orchestration/status", payload="DEPLOYMENT_COMPLETE", trace_id=message.trace_id)

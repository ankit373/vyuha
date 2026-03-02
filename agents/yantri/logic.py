from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger

class Yantri(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["mlops/input", "mlops/verified"]

    async def handle_message(self, message: Message):
        if message.topic == "mlops/input":
            logger.info(f"Yantri: Designing ML production infrastructure and monitoring strategy...")
            
            prompt = (
                "Act as a Lead MLOps Architect. Design a production-grade, governed machine learning infrastructure for: "
                f"{message.payload}. Focus on automated CI/CD for models, observability frameworks, and strict and compliant lineage tracking."
            )
            mlops_plan = await self.ask_ai(prompt)
            
            # Submit for review by Budhi (ML) and Arjuna (Deployment)
            await self.send_message(
                topic="mlops/draft",
                payload={"mlops_plan": mlops_plan},
                is_action=True,
                trace_id=message.trace_id
            )

        elif message.topic == "mlops/verified":
            logger.info(f"Yantri: MLOps infrastructure verified and ready for deployment.")
            await self.send_message(topic="deployment/input", payload=message.payload, trace_id=message.trace_id)

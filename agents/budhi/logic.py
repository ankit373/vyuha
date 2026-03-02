from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger

class Budhi(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["ml/input", "ml/verified", "review/Budhi"]

    async def handle_message(self, message: Message):
        if message.topic == "ml/input":
            logger.info(f"Budhi: Researching and designing ML models...")
            
            prompt = (
                "Act as a Principal ML Engineer. Propose an elite algorithmic architecture for: "
                f"{message.payload}. Focus on mathematical rigor, sophisticated feature engineering, and robust evaluation metrics."
            )
            ml_plan = await self.ask_ai(prompt)
            
            # Submit for review by Dharma (Standards) and Ganaka (Data)
            await self.send_message(
                topic="ml/draft",
                payload={"ml_plan": ml_plan},
                is_action=True,
                trace_id=message.trace_id
            )

        elif message.topic == "ml/verified":
            logger.info(f"Budhi: ML architecture verified. Notifying MLOps and Development.")
            await self.send_message(topic="mlops/input", payload=message.payload, trace_id=message.trace_id)
            await self.send_message(topic="development/ml_ready", payload=message.payload, trace_id=message.trace_id)

        elif message.topic == "review/Budhi":
            logger.info(f"Budhi: Reviewing {message.sender}'s ML infrastructure plan.")
            content = message.payload['content']
            review_prompt = f"Review this MLOps infrastructure for model compatibility and monitoring rigor: {content}. Respond 'APPROVED' or provide feedback."
            review_result = await self.ask_ai(review_prompt)
            
            if "APPROVED" in review_result.upper():
                from core.bus import bus
                await bus.approve(message.payload['original_message_id'], self.name)
            else:
                await self.send_message(topic=f"{message.sender}/feedback", payload=review_result, trace_id=message.trace_id)

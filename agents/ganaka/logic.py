from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger

class Ganaka(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["data/input", "data/verified", "review/Ganaka"]

    async def handle_message(self, message: Message):
        if message.topic == "data/input":
            logger.info(f"Ganaka: Designing ETL pipelines and data analysis strategy...")
            
            prompt = (
                "Act as a Lead Data Analyst. Architect an elite, large-scale ETL/ELT pipeline and data intelligence strategy for: "
                f"{message.payload}. Focus on data lineage, quality enforcement, and automated insight generation."
            )
            data_plan = await self.ask_ai(prompt)
            
            # Submit for review by Varuna (DBA) and Sutra (Requirements)
            await self.send_message(
                topic="data/draft",
                payload={"data_plan": data_plan},
                is_action=True,
                trace_id=message.trace_id
            )

        elif message.topic == "data/verified":
            logger.info(f"Ganaka: Data strategy verified. Notifying ML team.")
            await self.send_message(topic="ml/input", payload=message.payload, trace_id=message.trace_id)

        elif message.topic == "review/Ganaka":
            logger.info(f"Ganaka: Reviewing {message.sender}'s model plan for data alignment.")
            content = message.payload['content']
            review_prompt = f"Review this ML plan for data pipeline alignment and feature engineering quality: {content}. Respond 'APPROVED' or provide feedback."
            review_result = await self.ask_ai(review_prompt)
            
            if "APPROVED" in review_result.upper():
                from core.bus import bus
                await bus.approve(message.payload['original_message_id'], self.name)
            else:
                await self.send_message(topic=f"{message.sender}/feedback", payload=review_result, trace_id=message.trace_id)

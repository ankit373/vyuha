from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger

class Varuna(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["architecture/verified", "database/input", "database/verified", "review/Varuna"]

    async def handle_message(self, message: Message):
        if message.topic in ["architecture/verified", "database/input"]:
            logger.info(f"Varuna: Designing high-performance database schema and optimization strategy...")
            
            prompt = (
                "Act as a Lead Database Administrator. Architect a professional-grade, high-performance database schema and optimization strategy "
                f"for: {message.payload}. Focus on mission-critical data modeling (SQL/Vector), advanced indexing, and high-availability topologies."
            )
            db_plan = await self.ask_ai(prompt)
            
            # Submit for dual-review by Kavacha (Security) and Vishwakarma (Architect)
            await self.send_message(
                topic="database/draft",
                payload={"db_plan": db_plan},
                is_action=True,
                trace_id=message.trace_id
            )

        elif message.topic == "database/verified":
            logger.info(f"Varuna: Database architecture verified. Notifying Data and Development teams.")
            await self.send_message(topic="data/input", payload=message.payload, trace_id=message.trace_id)
            await self.send_message(topic="development/db_ready", payload=message.payload, trace_id=message.trace_id)

        elif message.topic == "review/Varuna":
            # Reviewing another agent's work (e.g., Ganaka's ETL plan)
            logger.info(f"Varuna: Reviewing {message.sender}'s work for DB compatibility.")
            content = message.payload['content']
            review_prompt = f"Review this ETL/Data plan for database compatibility and performance: {content}. Respond 'APPROVED' or provide feedback."
            review_result = await self.ask_ai(review_prompt)
            
            if "APPROVED" in review_result.upper():
                from core.bus import bus
                await bus.approve(message.payload['original_message_id'], self.name)
            else:
                await self.send_message(topic=f"{message.sender}/feedback", payload=review_result, trace_id=message.trace_id)

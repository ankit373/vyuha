from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger

class Pariksha(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["testing/input", "testing/verified"]

    async def handle_message(self, message: Message):
        if message.topic == "testing/input":
            logger.info(f"Pariksha: Generating test cases and QA strategy...")
            
            prompt = (
                "Act as a Lead QA Engineer. Design a comprehensive testing strategy and specific high-fidelity test cases (unit, integration, e2e) "
                f"for: {message.payload}. Focus on edge cases, performance benchmarks, and zero-defect validation. Output a technical QA report."
            )
            test_plan = await self.ask_ai(prompt)
            
            # Submit for review by Yantra and Sutra
            await self.send_message(
                topic="testing/draft",
                payload={"test_plan": test_plan},
                is_action=True,
                trace_id=message.trace_id
            )

        elif message.topic == "testing/verified":
            logger.info(f"Pariksha: Test suite verified. Running tests...")
            # Signal success to deployment
            await self.send_message(
                topic="deployment/input",
                payload=message.payload,
                trace_id=message.trace_id
            )

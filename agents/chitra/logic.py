from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger

class Chitra(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["ui/input", "ui/verified"]

    async def handle_message(self, message: Message):
        if message.topic == "ui/input":
            logger.info(f"Chitra: Designing UI/UX and visual assets...")
            
            prompt = (
                "Act as a Lead UI/UX Product Designer. Architect a premium, state-of-the-art visual language for: {message.payload}. "
                "Utilize rich aesthetics including glassmorphism, tailored color palettes, and elegant typography. Output detailed CSS definitions, "
                "structural HTML/React components, and specifications for micro-animations that deliver a 'WOW' user experience."
            )
            ui_design = await self.ask_ai(prompt)
            
            # Submit for review by Dharma
            await self.send_message(
                topic="ui/draft",
                payload={"ui_design": ui_design},
                is_action=True,
                trace_id=message.trace_id
            )

        elif message.topic == "ui/verified":
            logger.info(f"Chitra: UI design verified and ready.")
            # Store or finalize UI assets

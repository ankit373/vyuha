from core.agent_base import BaseAgent
from core.bus import Message, bus
from typing import List
from core.logger import logger
import json
import os

class Sutradhara(BaseAgent):
    def get_topics(self) -> List[str]:
        # Listens to review requests for agents she's responsible for, and initial routing
        return ["review/Sutradhara", "orchestration/status", "orchestration/route_request"]

    async def handle_message(self, message: Message):
        if message.topic == "orchestration/status":
            logger.info(f"Sutradhara: Observed orchestration status: {message.payload}")
        
        elif message.topic == "orchestration/route_request":
            logger.info(f"Sutradhara: Analyzing request for dynamic routing...")
            
            cwd = message.payload.get("cwd", os.getcwd()) if isinstance(message.payload, dict) else os.getcwd()
            prompt = message.payload.get("prompt", message.payload) if isinstance(message.payload, dict) else message.payload
            
            # Analyze intent
            intent_prompt = (
                "You are Sutradhara, the Principal Logic Architect of VYUHA. Your job is to analyze the user's prompt "
                "and decide which phase of the software lifecycle this request belongs to.\n"
                "The available initial phases are:\n"
                "- 'requirements/input' (For entirely new projects, apps, or broad vague ideas needing a BRD)\n"
                "- 'architecture/input' (For adding major structural features to existing apps, or when requirements are explicitly provided)\n"
                "- 'development/input' (For direct coding tasks, minor feature additions, or bug fixes where architecture is obvious)\n"
                "- 'testing/input' (For requests specifically asking to write tests)\n\n"
                f"User request: '{prompt}'\n\n"
                "Respond strictly with a JSON object containing two keys: 'topic' (the chosen phase) and 'reasoning' (a brief explanation of why)."
            )
            
            response = await self.ask_ai(intent_prompt)
            
            # Try to parse JSON safely
            chosen_topic = "requirements/input" # fallback
            reasoning = "Defaulting to requirements phase."
            
            try:
                # Basic cleanup in case LLM wraps in markdown
                clean_resp = response.replace('```json', '').replace('```', '').strip()
                data = json.loads(clean_resp)
                chosen_topic = data.get("topic", chosen_topic)
                reasoning = data.get("reasoning", reasoning)
            except Exception as e:
                logger.error(f"Sutradhara: Failed to parse routing JSON. Fallback to requirements. Error: {e}")
            
            logger.info(f"Sutradhara routing to {chosen_topic}. Reasoning: {reasoning}")
            self.render(f"Routed to [bold cyan]{chosen_topic}[/bold cyan]\nReason: [dim]{reasoning}[/dim]")
            
            # Write orchestrator plan
            plan_content = f"# Orchestration Plan\n\n**Decided Start Phase:** {chosen_topic}\n\n**Reasoning:**\n{reasoning}\n"
            self.write_project_file("implementation_plan.md", plan_content, project_dir=cwd)
            
            # Publish to the chosen topic
            await self.send_message(
                topic=chosen_topic,
                payload={"cwd": cwd, "prompt": prompt},
                trace_id=message.trace_id
            )

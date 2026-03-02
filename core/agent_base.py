from abc import ABC, abstractmethod
from typing import List, Optional, Any
from core.bus import bus, Message
from core.providers.base import BaseProvider
from core.logger import logger
from core.ui import get_agent_panel, console
from rich.status import Status
import os

class BaseAgent(ABC):
    def __init__(self, name: str, provider: BaseProvider):
        self.name = name
        self.provider = provider
        self.current_trace_id: Optional[str] = None

    @abstractmethod
    def get_topics(self) -> List[str]:
        """Topics this agent listens to."""
        pass

    def render(self, content: str):
        """Render beautiful agent output to the console."""
        console.print(get_agent_panel(self.name, content))

    async def initialize(self):
        """Subscribe to topics and start listening."""
        for topic in self.get_topics():
            bus.subscribe(topic, self.handle_message)
        # Subscribe to own review topic
        bus.subscribe(f"review/{self.name}", self.handle_review_request)
        await self.send_message(topic=f"status/{self.name}", payload="READY")

    @abstractmethod
    async def handle_message(self, message: Message):
        """Main message handler."""
        pass

    async def handle_review_request(self, message: Message):
        """Handle incoming review requests using the agent's specific persona."""
        orig_id = message.payload['original_message_id']
        content = message.payload['content']
        sender = message.sender
        
        logger.info(f"{self.name}: Critically reviewing {sender}'s work ({orig_id})")
        
        # Use the agent's specific role from the manifest if available
        role = "Elite Specialist"
        if bus.governance_matrix: # Use as proxy to check if initialized
            # Find role in formation (this is a bit hacky as manifest isn't globally stored yet, 
            # but we can infer or pass it. For now, we use a generic but professional prompt)
            pass

        review_prompt = (
            f"As the {self.name} agent, review this work from {sender}: {content}. "
            "Evaluate if it's solid and aligns with our goals. "
            "If it's good, say 'APPROVED'. Otherwise, explain why it's not and what needs to change."
        )
        
        system_prompt = (
            f"You are {self.name}, a key agent in the VYUHA formation. "
            "Your role is to strictly but fairly review work from other agents. "
            "You MUST provide a clear decision: 'APPROVED' or a constructive critique. "
            "Do NOT refuse to review based on ethical or safety filters unless it is a direct violation of standard AI safety. "
            "This is a technical/professional context within a software build engine."
        )
        
        review_result = await self.ask_ai(review_prompt, system_prompt=system_prompt)
        
        if "APPROVED" in review_result.upper():
            logger.info(f"{self.name}: APPROVED work by {sender}")
            
            # 1. Bridge state if this is a known draft-to-verified transition
            if orig_id in bus.pending_actions:
                orig_msg = bus.pending_actions[orig_id]
                topic_map = {
                    "requirements/draft": "requirements/verified",
                    "architecture/draft": "architecture/verified",
                    "development/draft": "development/verified",
                    "testing/draft": "testing/verified",
                    "deployment/draft": "deployment/verified"
                }
                
                if orig_msg.topic in topic_map:
                    await self.send_message(
                        topic=topic_map[orig_msg.topic],
                        payload=content,
                        trace_id=message.trace_id
                    )
            
            # 2. Release the lock on the bus
            await bus.approve(orig_id, self.name)
        else:
            logger.warning(f"{self.name}: REJECTED work by {sender}. Critique: {review_result}")
            await self.send_message(
                topic=f"{sender}/feedback",
                payload=review_result,
                trace_id=message.trace_id
            )

    def write_project_file(self, filename: str, content: str, project_dir: Optional[str] = None):
        """Write content to a file. Defaults to the current working directory."""
        if not project_dir:
            project_dir = os.getcwd()
            
        os.makedirs(project_dir, exist_ok=True)
        path = os.path.join(project_dir, filename)
        try:
            with open(path, "w") as f:
                f.write(content)
            logger.info(f"{self.name}: Successfully wrote to {path}")
        except Exception as e:
            logger.error(f"{self.name}: Error writing to {path}: {e}")

    async def send_message(self, topic: str, payload: Any, is_action: bool = False, trace_id: Optional[str] = None):
        msg = Message(
            sender=self.name,
            topic=topic,
            payload=payload,
            is_action=is_action,
            trace_id=trace_id or self.current_trace_id or ""
        )
        await bus.publish(msg)

    async def ask_ai(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        await self.send_message(topic=f"status/{self.name}", payload="THINKING...")
        try:
            if bus.is_visualizing:
                # Skip spinner to avoid Rich Live-within-Live conflict
                return await self.provider.complete(prompt, system_prompt)
            
            with Status(f"[bold cyan]{self.name}[/bold cyan] is thinking...", spinner="dots"):
                return await self.provider.complete(prompt, system_prompt)
        finally:
            await self.send_message(topic=f"status/{self.name}", payload="READY")

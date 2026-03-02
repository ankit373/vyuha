import asyncio
import uuid
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from core.logger import logger

@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    topic: str = ""
    payload: Any = None
    trace_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_action: bool = False
    approved_by: List[str] = field(default_factory=list)

class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.governance_matrix: Dict[str, List[str]] = {}
        self.review_modes: Dict[str, str] = {}
        self.pending_actions: Dict[str, Message] = {}
        self.listeners: List[Callable] = []
        self.active_tasks: set = set()
        self._lock = asyncio.Lock()
        self.is_visualizing = False

    def set_governance(self, matrix: Dict[str, List[str]], modes: Dict[str, str] = {}):
        """Set governance matrix and modes (CONSENSUS, MAJORITY, SINGLE)."""
        self.governance_matrix = matrix
        self.review_modes = modes # {agent_name: mode}

    def register_listener(self, callback: Callable):
        """Register a global listener for all bus activity (for visualizer)."""
        self.listeners.append(callback)

    def subscribe(self, topic: str, callback: Callable):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        logger.info(f"Subscribed to topic: {topic}")

    async def publish(self, message: Message):
        logger.info(f"Publishing message on topic '{message.topic}' from '{message.sender}'")
        
        # Notify global listeners
        for listener in self.listeners:
            try:
                listener(message)
            except Exception as e:
                logger.error(f"Listener error: {e}")
        
        # Check Governance for Actions
        if message.is_action:
            # SECURITY: Prevent unauthorized 'System' or 'User' actions from agents
            if message.sender in ["System", "User"]:
                logger.warning(f"SECURITY: Unauthorized action attempt from '{message.sender}' on topic '{message.topic}'")
                return

            reviewers = self.governance_matrix.get(message.sender, [])
            if reviewers:
                # If not approved yet, block and notify
                if not self._check_approval(message):
                    async with self._lock:
                        self.pending_actions[message.id] = message
                    
                    remaining = [r for r in reviewers if r not in message.approved_by]
                    logger.warning(f"Action from '{message.sender}' BLOCKED ({self.review_modes.get(message.sender, 'SINGLE')}). Needs: {remaining}")
                    await self._notify_reviewers(message, remaining)
                    return
                else:
                    logger.info(f"Action from '{message.sender}' is APPROVED. Proceeding to subscribers.")
                    # Clean up pending if it was there
                    async with self._lock:
                        if message.id in self.pending_actions:
                            del self.pending_actions[message.id]

        # Routine Message or Approved Action
        if message.topic in self.subscribers:
            for callback in self.subscribers[message.topic]:
                task = asyncio.create_task(self._safe_callback(callback, message))
                self.active_tasks.add(task)
                task.add_done_callback(self.active_tasks.discard)

    async def _safe_callback(self, callback: Callable, message: Message):
        try:
            await callback(message)
        except Exception as e:
            logger.error(f"Error in subscriber callback for topic '{message.topic}': {e}")

    def _check_approval(self, message: Message) -> bool:
        """Check if message meets governance requirements based on mode."""
        reviewers = self.governance_matrix.get(message.sender, [])
        mode = self.review_modes.get(message.sender, "SINGLE").upper()
        approvals = len(message.approved_by)
        total_needed = len(reviewers)

        if total_needed == 0: return True
        
        if mode == "SINGLE" and approvals >= 1: return True
        if mode == "CONSENSUS" and approvals >= total_needed: return True
        if mode == "MAJORITY" and approvals > total_needed / 2: return True
        if mode == "AUTO": return True
        
        return False

    async def approve(self, message_id: str, reviewer: str):
        if message_id in self.pending_actions:
            msg = self.pending_actions[message_id]
            if reviewer not in msg.approved_by:
                msg.approved_by.append(reviewer)
                logger.info(f"Message {message_id} approved by {reviewer}")
            
            if self._check_approval(msg):
                logger.info(f"Message {message_id} fully approved via {self.review_modes.get(msg.sender)}! Re-publishing...")
                del self.pending_actions[message_id]
                await self.publish(msg)

    async def _notify_reviewers(self, message: Message, reviewers: List[str]):
        """Special topic for governance review notifications."""
        for reviewer in reviewers:
            review_topic = f"review/{reviewer}"
            if review_topic in self.subscribers:
                review_msg = Message(
                    sender="System",
                    topic=review_topic,
                    payload={"original_message_id": message.id, "content": message.payload},
                    trace_id=message.trace_id
                )
                for callback in self.subscribers[review_topic]:
                    asyncio.create_task(callback(review_msg))

bus = MessageBus()

import pytest
import asyncio
from core.bus import bus, Message
from core.agent_base import BaseAgent
from core.providers.base import BaseProvider

class MockProvider(BaseProvider):
    async def complete(self, prompt, system_prompt=None):
        return "mocked response"
    async def chat(self, messages):
        return "mocked chat"
    def name(self):
        return "Mock"

class TestAgent(BaseAgent):
    def get_topics(self): return ["test/topic"]
    async def handle_message(self, message): pass

@pytest.mark.asyncio
async def test_agent_initialization_and_subscription():
    # RESET BUS
    bus.subscribers = {}
    
    provider = MockProvider()
    agent = TestAgent("TestAgent", provider)
    await agent.initialize()
    
    assert "test/topic" in bus.subscribers
    assert f"review/{agent.name}" in bus.subscribers

@pytest.mark.asyncio
async def test_agent_send_message_flow():
    # RESET BUS
    bus.subscribers = {}
    received_msgs = []
    
    async def dummy_handler(m):
        received_msgs.append(m)
    
    bus.subscribe("data/topic", dummy_handler)
    
    provider = MockProvider()
    agent = TestAgent("SenderAgent", provider)
    await agent.send_message("data/topic", "hello world")
    
    await asyncio.sleep(0.1)
    assert len(received_msgs) == 1
    assert received_msgs[0].payload == "hello world"
    assert received_msgs[0].sender == "SenderAgent"

@pytest.mark.asyncio
async def test_agent_ask_ai_proxy():
    provider = MockProvider()
    agent = TestAgent("AIAgent", provider)
    response = await agent.ask_ai("What is 1+1?")
    assert response == "mocked response"

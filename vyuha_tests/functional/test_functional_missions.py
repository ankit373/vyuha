import pytest
import asyncio
import json
from core.bus import bus, Message
from agents.sutra.logic import Sutra
from agents.yantra.logic import Yantra
from core.providers.base import BaseProvider

class MockProvider(BaseProvider):
    async def complete(self, prompt, system_prompt=None):
        # Return valid JSON for agents expecting it
        return json.dumps({"result": "success", "data": "mock_data"})
    async def chat(self, messages): return "mock"
    def name(self): return "Mock"

@pytest.mark.asyncio
async def test_software_build_initial_phase():
    """Simulate the initial phase of a software build mission."""
    # RESET BUS
    bus.subscribers = {}
    bus.pending_actions = {}
    bus.set_governance({"Sutra": ["Sutradhara"]}, {"Sutra": "SINGLE"})
    
    provider = MockProvider()
    sutra = Sutra(name="Sutra", provider=provider)
    await sutra.initialize()
    
    # Track draft topic
    drafts = []
    async def draft_handler(m): drafts.append(m)
    bus.subscribe("requirements/draft", draft_handler)

    # USER INITIATES
    await bus.publish(Message(sender="User", topic="requirements/input", payload="Build e-commerce"))
    
    await asyncio.sleep(0.1)
    # Sutra should have published a draft marked as action
    assert len(drafts) == 0 # Should be BLOCKED in pending_actions
    assert len(bus.pending_actions) == 1
    
    # APPROVE BY SUTRADHARA
    msg_id = list(bus.pending_actions.keys())[0]
    await bus.approve(msg_id, "Sutradhara")
    
    await asyncio.sleep(0.1)
    assert len(drafts) == 1
    assert "brd" in drafts[0].payload

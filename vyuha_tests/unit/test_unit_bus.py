import pytest
import asyncio
from core.bus import Message, MessageBus

@pytest.fixture
def bus():
    return MessageBus()

@pytest.mark.asyncio
async def test_publish_subscribe_success(bus):
    received = []
    async def handler(msg):
        received.append(msg)
    
    bus.subscribe("unit/test", handler)
    msg = Message(sender="TestAgent", topic="unit/test", payload="data")
    await bus.publish(msg)
    
    await asyncio.sleep(0.1)
    assert len(received) == 1
    assert received[0].payload == "data"
    assert len(bus.active_tasks) == 0

@pytest.mark.asyncio
async def test_security_sender_bypass_blocked(bus):
    """Verify that agents cannot impersonate System or User for actions."""
    bus.set_governance({"System": ["R1"]}, {"System": "SINGLE"})
    msg = Message(sender="System", topic="admin/topic", payload="evil", is_action=True)
    await bus.publish(msg)
    
    await asyncio.sleep(0.1)
    # Should be blocked by security check before reaching governance
    assert msg.id not in bus.pending_actions

@pytest.mark.asyncio
async def test_error_handling_in_callbacks(bus):
    """Verify that one failing callback doesn't crash the bus."""
    success_callback_called = False
    
    async def failing_handler(msg):
        raise RuntimeError("Boom")
        
    async def success_handler(msg):
        nonlocal success_callback_called
        success_callback_called = True

    bus.subscribe("test/topic", failing_handler)
    bus.subscribe("test/topic", success_handler)
    
    await bus.publish(Message(sender="User", topic="test/topic", payload="trigger"))
    await asyncio.sleep(0.1)
    
    assert success_callback_called is True
    assert len(bus.active_tasks) == 0

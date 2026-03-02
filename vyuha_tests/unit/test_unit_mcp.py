import pytest
from core.mcp import MCPClient, init_mcp

@pytest.mark.asyncio
async def test_mcp_client_initialization():
    configs = [{"name": "test-server", "url": "http://localhost:8080"}]
    client = MCPClient(configs)
    await client.connect_all()
    
    assert "test-server" in client.connected_servers
    assert client.connected_servers["test-server"]["status"] == "connected"

@pytest.mark.asyncio
async def test_mcp_tool_retrieval():
    configs = [{"name": "s1", "url": "url"}]
    client = MCPClient(configs)
    await client.connect_all()
    
    tools = await client.get_tools()
    assert len(tools) == 2
    assert tools[0]["name"] == "s1_search"

@pytest.mark.asyncio
async def test_mcp_tool_call():
    configs = [{"name": "s1", "url": "url"}]
    client = MCPClient(configs)
    await client.connect_all()
    
    response = await client.call_tool("s1", "s1_search", {"q": "test"})
    assert response["status"] == "success"
    assert "Mock output" in response["output"]

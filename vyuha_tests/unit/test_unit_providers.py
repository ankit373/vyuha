import pytest
from core.providers.ollama import OllamaProvider
from core.providers.gemini import GeminiProvider
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.fixture
def mock_httpx_client():
    """Fixture to provide a mocked httpx.AsyncClient."""
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        yield mock_client

@pytest.mark.asyncio
async def test_ollama_provider_completion(mock_httpx_client):
    provider = OllamaProvider(model="llama3")
    
    # Mock the post response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "test response"}
    
    mock_httpx_client.post.return_value = mock_response
    
    response = await provider.complete("hello")
    assert response == "test response"

@pytest.mark.asyncio
async def test_gemini_provider_completion(mock_httpx_client):
    provider = GeminiProvider(model="gemini-1.5", api_key="test-key")
    
    # Mock the post response with the complex Gemini structure
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'candidates': [
            {'content': {'parts': [{'text': 'gemini response'}]}}
        ]
    }
    
    mock_httpx_client.post.return_value = mock_response
    
    response = await provider.complete("hello")
    assert response == "gemini response"

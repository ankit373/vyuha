import pytest
import os
import json
from core.config import Config

@pytest.fixture
def temp_manifest(tmp_path):
    d = tmp_path / "core"
    d.mkdir()
    f = d / "a2a.json"
    content = {
        "project": "VYUHA",
        "version": "1.0",
        "protocol": "A2A",
        "formation": {
            "Suite": {"Agent": {"review_mode": "SINGLE"}}
        }
    }
    f.write_text(json.dumps(content))
    return f

def test_config_manifest_validation_success(temp_manifest):
    config = Config()
    manifest = config.load_a2a_manifest(str(temp_manifest))
    assert manifest["project"] == "VYUHA"

def test_config_manifest_validation_failure(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps({"bad": "key"}))
    config = Config()
    manifest = config.load_a2a_manifest(str(f))
    assert manifest == {} # Should return empty on validation error

def test_save_api_key_idempotency(tmp_path):
    env_file = tmp_path / ".env"
    config = Config()
    
    # Implementation uses relative path ".env", we might need to mock or change directory
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        config.save_api_key("key1", "gemini")
        config.save_api_key("key2", "gemini")
        
        content = env_file.read_text()
        assert content.count("GEMINI_API_KEY") == 1
        assert "GEMINI_API_KEY=key2" in content
    finally:
        os.chdir(original_cwd)

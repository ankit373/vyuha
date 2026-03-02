import os
import yaml
import json
from dotenv import load_dotenv
from core.logger import logger

# Load environment variables from .env if it exists
load_dotenv()

DEFAULT_CONFIG = {
    "provider": "ollama",
    "model": "llama3.2:1b",
    "api_key": None,
    "base_url": None,
    "log_level": "INFO",
    "mcp_servers": [],
}

GLOBAL_CONFIG_DIR = os.path.expanduser("~/.vyuha")
GLOBAL_CONFIG_PATH = os.path.join(GLOBAL_CONFIG_DIR, "config.yaml")

class Config:
    def __init__(self, config_path="config.yaml"):
        self.settings = DEFAULT_CONFIG.copy()
        
        # Priority: Local config.yaml > ~/.vyuha/config.yaml
        if os.path.exists(config_path):
            self.load_from_yaml(config_path)
        elif os.path.exists(GLOBAL_CONFIG_PATH):
            self.load_from_yaml(GLOBAL_CONFIG_PATH)
            
        self.load_from_env()

    def load_from_yaml(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        self.settings.update(yaml_config)
            except Exception as e:
                logger.error(f"Failed to load config from {path}: {e}")

    def load_from_env(self):
        # Environment variables take precedence
        if os.getenv("VYUHA_PROVIDER"):
            self.settings["provider"] = os.getenv("VYUHA_PROVIDER")
        if os.getenv("VYUHA_MODEL"):
            self.settings["model"] = os.getenv("VYUHA_MODEL")
        if os.getenv("VYUHA_API_KEY"):
            self.settings["api_key"] = os.getenv("VYUHA_API_KEY")
        if os.getenv("VYUHA_LOG_LEVEL"):
            self.settings["log_level"] = os.getenv("VYUHA_LOG_LEVEL")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def update(self, key, value):
        self.settings[key] = value

    def save_to_yaml(self, path=None):
        if path is None:
            # If local config exists, update it. Otherwise use global.
            path = "config.yaml" if os.path.exists("config.yaml") else GLOBAL_CONFIG_PATH
            
        # Ensure global dir exists if saving there
        if path == GLOBAL_CONFIG_PATH:
            os.makedirs(GLOBAL_CONFIG_DIR, exist_ok=True)
        try:
            # We only save provider and model to yaml for now
            to_save = {
                "provider": self.settings.get("provider"),
                "model": self.settings.get("model"),
                "log_level": self.settings.get("log_level")
            }
            with open(path, "w") as f:
                yaml.dump(to_save, f)
            logger.info(f"Configuration saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save config to {path}: {e}")

    def save_api_key(self, api_key, provider):
        """Save API key to .env file securely."""
        env_key = f"VYUHA_{provider.upper()}_API_KEY"
        if provider.lower() == "gemini":
            env_key = "GEMINI_API_KEY"
        elif provider.lower() == "openai":
            env_key = "OPENAI_API_KEY"
            
        try:
            # Check if key already exists to prevent duplicates
            lines = []
            if os.path.exists(".env"):
                with open(".env", "r") as f:
                    lines = f.readlines()
            
            new_lines = [line for line in lines if not line.startswith(f"{env_key}=")]
            new_lines.append(f"{env_key}={api_key}\n")
            
            with open(".env", "w") as f:
                f.writelines(new_lines)
                
            logger.info(f"API key for {provider} saved/updated in .env")
            # Reload env
            load_dotenv(override=True)
            self.load_from_env()
        except Exception as e:
            logger.error(f"Failed to save API key to .env: {e}")

    def load_a2a_manifest(self, path="core/a2a.json"):
        """Load and validate the A2A governance manifest."""
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    manifest = json.load(f)
                    self._validate_manifest(manifest)
                    return manifest
            except Exception as e:
                logger.error(f"Failed to load or validate A2A manifest: {e}")
        return {}

    def _validate_manifest(self, manifest):
        """Basic validation for the A2A manifest structure."""
        required_keys = ["project", "version", "protocol", "formation"]
        for key in required_keys:
            if key not in manifest:
                raise ValueError(f"Missing required manifest key: {key}")
        
        if not isinstance(manifest["formation"], dict):
            raise ValueError("'formation' must be a dictionary.")

    def get_governance_matrix(self):
        """Extract governance matrix from A2A manifest."""
        manifest = self.load_a2a_manifest()
        matrix = {}
        formation = manifest.get("formation", {})
        for suite in formation.values():
            for agent_name, details in suite.items():
                matrix[agent_name] = details.get("reviewers", [])
        return matrix
    def get_governance_modes(self):
        """Extract review modes from A2A manifest."""
        manifest = self.load_a2a_manifest()
        modes = {}
        formation = manifest.get("formation", {})
        for suite in formation.values():
            for agent_name, details in suite.items():
                modes[agent_name] = details.get("review_mode", "SINGLE")
        return modes

    def add_mcp_server(self, name, url):
        """Add an MCP server to the configuration and save."""
        mcp_list = self.settings.get("mcp_servers", [])
        # Check for duplicates
        if any(s.get("name") == name for s in mcp_list):
            return False
        
        mcp_list.append({"name": name, "url": url})
        self.settings["mcp_servers"] = mcp_list
        self.save_to_yaml()
        return True

# Global config instance
config = Config()

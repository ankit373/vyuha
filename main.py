import asyncio
import typer
import os
from core.logger import logger
from core.config import config, GLOBAL_CONFIG_PATH
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED
from core.bus import bus, Message
from core.visualizer import FormationVisualizer
from core.ui import print_banner, get_agent_panel, print_interaction, print_success, print_step, console

# Import agents
from agents.sutra.logic import Sutra
from agents.sutradhara.logic import Sutradhara
from agents.dharma.logic import Dharma
from agents.vishwakarma.logic import Vishwakarma
from agents.yantra.logic import Yantra
from agents.kavacha.logic import Kavacha
from agents.lipi.logic import Lipi
from agents.akasha.logic import Akasha
from agents.chitra.logic import Chitra
from agents.pariksha.logic import Pariksha
from agents.arjuna.logic import Arjuna
from agents.prithvi.logic import Prithvi
from agents.varuna.logic import Varuna
from agents.ganaka.logic import Ganaka
from agents.budhi.logic import Budhi
from agents.yantri.logic import Yantri

app = typer.Typer(help="VYUHA: Elite Agent Engine", no_args_is_help=True)
console = Console()

from core.mcp import init_mcp

# Load Governance from A2A Manifest
GOVERNANCE_MATRIX = config.get_governance_matrix()
GOVERNANCE_MODES = config.get_governance_modes()

async def run_system(prompt: str):
    # Core initialization
    bus.set_governance(GOVERNANCE_MATRIX, GOVERNANCE_MODES)
    
    # The system now operates in the Current Working Directory just like a local dev assistant.
    cwd = os.getcwd()
    # If the user included --name (legacy), we just treat it as part of the prompt


    # 1. Initialize Visualizer EARLY to capture all bus traffic
    viz = FormationVisualizer()
    bus.register_listener(viz.on_bus_message)
    
    # 2. Inform the bus about current provider
    provider_name = config.get("provider")
    model_name = config.get("model")
    api_key = config.get("api_key")
    
    await bus.publish(Message(
        sender="System", 
        topic="status/provider", 
        payload={"provider": provider_name, "model": model_name}
    ))
    await bus.publish(Message(sender="System", topic="system/status", payload="Initializing Resources..."))

    # Initialize MCP Servers
    mcp_configs = config.get("mcp_servers", [])
    if mcp_configs:
        await init_mcp(mcp_configs)
        logger.info(f"MCP Servers initialized: {len(mcp_configs)}")
    
    if provider_name == "gemini":
        from core.providers.gemini import GeminiProvider
        provider = GeminiProvider(model=model_name, api_key=api_key)
    else:
        from core.providers.ollama import OllamaProvider
        provider = OllamaProvider(model=model_name)
    
    await bus.publish(Message(sender="System", topic="system/status", payload="Deploying Agents..."))

    agents = [
        Sutra(name="Sutra", provider=provider),
        Sutradhara(name="Sutradhara", provider=provider),
        Dharma(name="Dharma", provider=provider),
        Kavacha(name="Kavacha", provider=provider),
        Vishwakarma(name="Vishwakarma", provider=provider),
        Yantra(name="Yantra", provider=provider),
        Lipi(name="Lipi", provider=provider),
        Akasha(name="Akasha", provider=provider),
        Chitra(name="Chitra", provider=provider),
        Pariksha(name="Pariksha", provider=provider),
        Arjuna(name="Arjuna", provider=provider),
        Prithvi(name="Prithvi", provider=provider),
        Varuna(name="Varuna", provider=provider),
        Ganaka(name="Ganaka", provider=provider),
        Budhi(name="Budhi", provider=provider),
        Yantri(name="Yantri", provider=provider),
    ]
    
    for agent in agents:
        await agent.initialize()

    async def build_mission():
        await bus.publish(Message(sender="System", topic="system/status", payload=f"Starting Mission Flow in {cwd}..."))
        logger.info(f"System ready. Triggering build loop for: {prompt}")
        await bus.publish(Message(sender="User", topic="orchestration/route_request", payload={"cwd": cwd, "prompt": prompt}))
        # Keep alive to see the flow
        while True:
            await asyncio.sleep(5)

    await viz.run(build_mission())

def check_setup():
    """Interactively check and setup provider/API keys."""
    provider = config.get("provider")
    model = config.get("model")
    
    config_exists = os.path.exists("config.yaml") or os.path.exists(GLOBAL_CONFIG_PATH)
    
    if not config_exists:
        print_banner()
        print_interaction("No configuration found. VYUHA works best with Gemini or OpenAI.")
        
        if typer.confirm("Would you like to configure an advanced AI provider (Gemini/OpenAI)?", default=True):
            provider = typer.prompt("Select Provider", type=str, default="gemini").lower()
            if provider == "gemini":
                model = "gemini-1.5-flash"
            elif provider == "openai":
                model = "gpt-4o"
            
            config.update("provider", provider)
            config.update("model", model)
            config.save_to_yaml()
            print_success(f"Configuration updated: {provider} ({model})")
        else:
            print_interaction("Defaulting to [bold]Ollama[/bold] (local models).")
            provider = "ollama"
            config.update("provider", "ollama")
            config.save_to_yaml()
            print_success("Using Ollama (local). Ensure Ollama is running.")

    if provider in ["gemini", "openai"]:
        api_key = os.getenv("GEMINI_API_KEY") if provider == "gemini" else os.getenv("OPENAI_API_KEY")
        if not api_key:
            print_interaction(f"Missing API Key for {provider.capitalize()}.")
            new_key = typer.prompt(f"Please enter your {provider.capitalize()} API Key", hide_input=True)
            if new_key:
                config.save_api_key(new_key, provider)
                print_success(f"API key for {provider} securely saved to .env")

mcp_app = typer.Typer(help="Manage MCP Servers")
app.add_typer(mcp_app, name="mcp")

@mcp_app.command(name="add")
def mcp_add(name: str, url: str):
    """Register a new MCP server with VYUHA."""
    if config.add_mcp_server(name, url):
        print_success(f"MCP Server '{name}' added successfully!")
    else:
        console.print(f"[bold red]Error:[/bold red] Server with name '{name}' already exists.")

@mcp_app.command(name="list")
def mcp_list():
    """List all registered MCP servers."""
    servers = config.get("mcp_servers", [])
    if not servers:
        console.print("No MCP servers registered.")
        return
    
    table = Table(title="Registered MCP Servers", box=ROUNDED)
    table.add_column("Name", style="bold cyan")
    table.add_column("URL", style="dim")
    for s in servers:
        table.add_row(s["name"], s["url"])
    console.print(table)

@app.command(name="start")
def start(prompt: str):
    """Interactively setup and start the multi-agent build process."""
    check_setup()
    print_banner()
    try:
        asyncio.run(run_system(prompt))
    except RuntimeError:
        # Fallback for environments with existing loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_system(prompt))

@app.command(name="build", hidden=True)
def build(prompt: str):
    """Legacy command alias for start."""
    try:
        asyncio.run(run_system(prompt))
    except RuntimeError:
        # Fallback for environments with existing loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_system(prompt))

@app.command(name="logs")
def show_logs(lines: int = 20):
    """Show the latest system logs."""
    if os.path.exists("vyuha.log"):
        with open("vyuha.log", "r") as f:
            content = f.readlines()
            for line in content[-lines:]:
                print(line.strip())
    else:
        print("No log file found.")

@app.command(name="visualize")
def visualize():
    """Launch the VYUHA formation visualizer in standalone mode."""
    viz = FormationVisualizer()
    async def dummy_mission():
        logger.info("Visualizer started in standalone mode. Waiting...")
        await asyncio.sleep(10)
    try:
        asyncio.run(viz.run(dummy_mission()))
    except RuntimeError:
        # Fallback for environments with existing loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(viz.run(dummy_mission()))

if __name__ == "__main__":
    app()

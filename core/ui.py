from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.box import ROUNDED

console = Console()

# VYUHA ASCII LOGO
VYUHA_LOGO = """
[bold cyan]
██╗   ██╗██╗   ██╗██╗   ██╗██╗  ██╗ █████╗ 
██║   ██║╚██╗ ██╔╝██║   ██║██║  ██║██╔══██╗
██║   ██║ ╚████╔╝ ██║   ██║███████║███████║
╚██╗ ██╔╝  ╚██╔╝  ██║   ██║██╔══██║██╔══██║
 ╚████╔╝    ██║   ╚██████╔╝██║  ██║██║  ██║
  ╚═══╝     ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
[/bold cyan]
[dim]Elite High-Governance Multi-Agent Engine[/dim]
"""

# AGENT ICONS & THEMES
AGENT_ASSETS = {
    "Sutra": {"icon": "📜", "color": "cyan", "title": "Lead Requirements Engineer"},
    "Dharma": {"icon": "⚖️", "color": "blue", "title": "Principal Standards Architect"},
    "Kavacha": {"icon": "🛡️", "color": "red", "title": "Chief Security Auditor"},
    "Akasha": {"icon": "🌐", "color": "magenta", "title": "Lead Connectivity Architect"},
    "Sutradhara": {"icon": "💠", "color": "white", "title": "Principal Logic Architect"},
    "Vishwakarma": {"icon": "🏗️", "color": "green", "title": "Senior Principal Architect"},
    "Yantra": {"icon": "⚙️", "color": "yellow", "title": "Lead Software Engineer"},
    "Chitra": {"icon": "🎨", "color": "bright_magenta", "title": "Lead UI/UX Designer"},
    "Pariksha": {"icon": "🧪", "color": "bright_green", "title": "Lead QA Engineer"},
    "Arjuna": {"icon": "🏹", "color": "bright_red", "title": "Lead DevOps Engineer"},
    "Prithvi": {"icon": "🌍", "color": "green", "title": "Lead Infrastructure Architect"},
    "Lipi": {"icon": "🖋️", "color": "blue", "title": "Senior Technical Scribe"},
    "Varuna": {"icon": "🌊", "color": "bright_blue", "title": "Lead Database Administrator"},
    "Ganaka": {"icon": "📊", "color": "bright_yellow", "title": "Lead Data Analyst"},
    "Budhi": {"icon": "🧠", "color": "purple", "title": "Principal ML Engineer"},
    "Yantri": {"icon": "🚀", "color": "bright_cyan", "title": "Lead MLOps Architect"},
}

def print_banner():
    console.print(VYUHA_LOGO, justify="center")

def get_agent_panel(name: str, content: str):
    asset = AGENT_ASSETS.get(name, {"icon": "🤖", "color": "white", "title": "Agent"})
    return Panel(
        content,
        title=f"{asset['icon']} [bold {asset['color']}]{name}[/bold {asset['color']}] | {asset['title']}",
        border_style=asset['color'],
        box=ROUNDED
    )

def print_interaction(prompt_text: str):
    """Beautified interaction prompt logic."""
    console.print(f"\n[bold white]VYUHA Query[/bold white] [dim]──────────────[/dim]")
    console.print(f"[bold cyan]?[/bold cyan] {prompt_text}")

def print_success(message: str):
    console.print(f"[bold green]✔[/bold green] {message}")

def print_step(message: str):
    console.print(f"[bold magenta]→[/bold magenta] {message}")

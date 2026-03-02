import asyncio
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.box import ROUNDED
from rich.text import Text
from rich.status import Status
from core.bus import Message, bus
from core.ui import AGENT_ASSETS, VYUHA_LOGO
from typing import Dict, List
import time

class FormationVisualizer:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.agent_statuses: Dict[str, str] = {
            "Sutra": "IDLE", "Dharma": "IDLE", "Kavacha": "IDLE", "Akasha": "IDLE",
            "Sutradhara": "IDLE", "Vishwakarma": "IDLE", "Yantra": "IDLE", "Chitra": "IDLE",
            "Pariksha": "IDLE", "Arjuna": "IDLE", "Prithvi": "IDLE", "Lipi": "IDLE",
            "Varuna": "IDLE", "Ganaka": "IDLE", "Budhi": "IDLE", "Yantri": "IDLE"
        }
        self.message_log: List[str] = []
        self.pending_actions: List[Dict] = []
        self.system_status: str = "Initializing Agents..."
        self.provider: str = "Unknown"
        self.model: str = "Unknown"
        self.start_time = time.time()

    def make_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=11),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )
        layout["main"].split_row(
            Layout(name="formation", ratio=2),
            Layout(name="side", ratio=1)
        )
        layout["side"].split_column(
            Layout(name="logs"),
            Layout(name="governance")
        )
        return layout

    def on_bus_message(self, message: Message):
        # Handle status/provider for UI header
        if message.topic == "status/provider":
            self.provider = message.payload.get("provider", "Unknown")
            self.model = message.payload.get("model", "Unknown")
            return

        # Handle special 'system/status' topic
        if message.topic == "system/status":
            self.system_status = str(message.payload)
            self.message_log.append(f"[{time.strftime('%H:%M:%S')}] SYSTEM: {message.payload}")
            return

        # Update agent status based on interaction
        sender = message.sender
        if sender in self.agent_statuses:
            if message.is_action:
                self.agent_statuses[sender] = "[bold yellow]ACTING[/bold yellow]"
            elif message.topic.startswith("status/"):
                self.agent_statuses[sender] = f"[bold cyan]{message.payload}[/bold cyan]"
            else:
                self.agent_statuses[sender] = "[bold green]BUSY[/bold green]"
        
        # Log message with payload hint
        payload_hint = str(message.payload)[:30] + "..." if message.payload else ""
        log_entry = f"[{time.strftime('%H:%M:%S')}] {sender} -> {message.topic} ({payload_hint})"
        self.message_log.append(log_entry)
        if len(self.message_log) > 10:
            self.message_log.pop(0)

        # Track pending governance
        if message.is_action:
            reviewers = bus.governance_matrix.get(sender, [])
            self.pending_actions.append({
                "id": message.id[:8],
                "agent": sender,
                "reviewers": reviewers,
                "approved_by": message.approved_by,
                "topic": message.topic
            })

    def generate_agent_grid(self) -> Table:
        table = Table(title="16 Lead Agents in Formation", border_style="cyan", box=ROUNDED)
        table.add_column("Suite", style="bold")
        table.add_column("Agent Leader", style="bold cyan")
        table.add_column("Status")

        suites = {
            "Core Dev": ["Sutra", "Dharma", "Kavacha", "Akasha"],
            "Architect": ["Sutradhara", "Vishwakarma", "Yantra", "Lipi"],
            "Project Ops": ["Chitra", "Pariksha", "Arjuna", "Prithvi"],
            "Data & ML": ["Varuna", "Ganaka", "Budhi", "Yantri"]
        }

        for suite, agents in suites.items():
            for agent in agents:
                asset = AGENT_ASSETS.get(agent, {"icon": "🤖", "color": "white"})
                status = self.agent_statuses.get(agent, "IDLE")
                table.add_row(suite, f"{asset['icon']} [bold {asset['color']}]{agent}[/bold {asset['color']}]", status)
                suite = "" # Only show suite name once
        return table

    def generate_log_panel(self) -> Panel:
        log_text = Text("\n".join(self.message_log))
        return Panel(log_text, title="A2A Bus Activity", border_style="magenta")

    def generate_governance_panel(self) -> Panel:
        table = Table(title="Governance Lockouts", border_style="red")
        table.add_column("ID", style="dim")
        table.add_column("Agent")
        table.add_column("Status")

        for action in self.pending_actions[-5:]:
            remaining = [r for r in action["reviewers"] if r not in action["approved_by"]]
            status = f"Waiting for: {', '.join(remaining)}" if remaining else "[bold green]APPROVED[/bold green]"
            table.add_row(action["id"], action["agent"], status)
        
        return Panel(table, border_style="red")

    def update_render(self) -> Layout:
        runtime = round(time.time() - self.start_time, 1)
        header_text = (
            f"[bold cyan]VYUHA Intelligence Controller[/bold cyan] | Runtime: {runtime}s | "
            f"Provider: [bold yellow]{self.provider}[/bold yellow] ([dim]{self.model}[/dim])"
        )
        status_line = f"Status: [bold green]{self.system_status}[/bold green]"
        
        # Combine logo and header text
        full_header = f"{VYUHA_LOGO.strip()}\n\n{header_text}\n{status_line}"
        
        self.layout["header"].update(Panel(full_header, border_style="cyan"))
        self.layout["footer"].update(Panel("[dim]A2A Protocol v2.0 | Elite Governance Active | Autonomous Mode[/dim]", border_style="cyan"))
        self.layout["formation"].update(self.generate_agent_grid())
        self.layout["logs"].update(self.generate_log_panel())
        self.layout["governance"].update(self.generate_governance_panel())
        return self.layout

    async def run(self, build_coro):
        """Run the visualizer alongside the build process."""
        self.start_time = time.time()
        bus.register_listener(self.on_bus_message)
        self.layout = self.make_layout()
        bus.is_visualizing = True
        
        async def refresh_loop():
            while bus.is_visualizing:
                self.update_render()
                await asyncio.sleep(0.2)

        refresh_task = asyncio.create_task(refresh_loop())
        
        try:
            with Live(self.layout, refresh_per_second=4, screen=True) as live:
                try:
                    # Give the UI a moment to initialize before triggering agents
                    await asyncio.sleep(0.5)
                    await build_coro
                except Exception as e:
                    error_msg = f"[bold red]FATAL ERROR: {str(e)}[/bold red]"
                    self.message_log.append(error_msg)
                    logger.error(f"Visualizer build error: {e}")
                    # Keep open longer on error
                    await asyncio.sleep(15)
                    return
                
                # Keep open for a few seconds to see final state
                await asyncio.sleep(5)
        finally:
            bus.is_visualizing = False
            refresh_task.cancel()

from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger
from core.disk import disk_service
import os

class Vishwakarma(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["architecture/input", "architecture/verified"]

    async def handle_message(self, message: Message):
        if message.topic == "architecture/input":
            logger.info(f"Vishwakarma: Designing architecture for spec {message.trace_id}")

            cwd = message.payload.get("cwd", os.getcwd()) if isinstance(message.payload, dict) else os.getcwd()
            spec_content = message.payload.get("brd", message.payload) if isinstance(message.payload, dict) else message.payload

            # 0. Scan existing project context
            logger.info(f"Vishwakarma: Scanning existing project files in {cwd}...")
            context = disk_service.scan_project_context(cwd)
            file_tree = context["file_tree"]
            file_contents = context["file_contents"]

            existing_context_str = ""
            if file_tree:
                tree_str = "\n".join(f"  - {f}" for f in file_tree[:60])
                existing_context_str = f"\n\n**EXISTING PROJECT FILES:**\n{tree_str}\n"
                if file_contents:
                    existing_context_str += "\n**KEY EXISTING FILE CONTENTS:**\n"
                    for path, content in list(file_contents.items())[:10]:
                        existing_context_str += f"\n### {path}\n```\n{content[:800]}\n```\n"
                existing_context_str += "\nDo NOT recreate files that already exist unless the spec requires changes to them. Extend existing code."

            # 1. Draft Architecture Blueprint
            arch_prompt = (
                "Act as a Senior Principal Architect. Design a production-grade architecture blueprint, including granular module structures, "
                f"DB relationships, and system boundaries for this requirement: {spec_content}. Provide a high-fidelity Mermaid diagram "
                "and an exhaustive list of all necessary files and their responsibilities."
                f"{existing_context_str}"
            )
            blueprint = await self.ask_ai(arch_prompt)

            # Save to architecture.md
            self.write_project_file("architecture.md", blueprint, project_dir=cwd)

            # 2. Submit for Review by Dharma
            payload = {"blueprint": blueprint, "cwd": cwd}
            await self.send_message(
                topic="architecture/draft",
                payload=payload,
                is_action=True,
                trace_id=message.trace_id
            )

        elif message.topic == "architecture/verified":
            logger.info(f"Vishwakarma: Architecture verified. Notifying Yantra.")
            await self.send_message(
                topic="development/input",
                payload=message.payload,
                trace_id=message.trace_id
            )


from core.agent_base import BaseAgent
from core.bus import Message
from typing import List, Any
from core.logger import logger
from core.disk import disk_service
import json
import os

class Sutra(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["requirements/input", "requirements/verified"]

    async def handle_message(self, message: Message):
        if message.topic == "requirements/input":
            logger.info(f"Sutra: Distilling requirements for: {message.payload}")

            cwd = message.payload.get("cwd", os.getcwd()) if isinstance(message.payload, dict) else os.getcwd()
            prompt = message.payload.get("prompt", message.payload) if isinstance(message.payload, dict) else message.payload

            # 0. Scan existing project context
            logger.info(f"Sutra: Scanning existing project files in {cwd}...")
            context = disk_service.scan_project_context(cwd)
            file_tree = context["file_tree"]
            file_contents = context["file_contents"]

            existing_context_str = ""
            if file_tree:
                tree_str = "\n".join(f"  - {f}" for f in file_tree[:60])
                existing_context_str = f"\n\n**EXISTING PROJECT FILES (already in the directory):**\n{tree_str}\n"
                if file_contents:
                    existing_context_str += "\n**EXISTING FILE CONTENTS (read for context):**\n"
                    for path, content in list(file_contents.items())[:10]:
                        existing_context_str += f"\n### {path}\n```\n{content[:800]}\n```\n"
                existing_context_str += "\nIf files already exist, build on top of them rather than starting from scratch."

            # 1. Draft a Plan (BRD) with existing context injected
            plan_prompt = (
                "Act as a Lead Requirements Engineer. Create a high-fidelity, comprehensive BRD (Business Requirements Document) "
                f"for the following high-level prompt: {prompt}. Focus on detailed features, edge cases, scalability constraints, "
                "and explicit success criteria. Output in a professional, structured JSON format."
                f"{existing_context_str}"
            )
            brd = await self.ask_ai(plan_prompt)
            self.render(f"Drafted BRD for project: [bold]{prompt}[/bold]\n\n[dim]{brd[:200]}...[/dim]")

            # 2. Save to implementation_plan.md
            self.write_project_file("implementation_plan.md", brd, project_dir=cwd)

            # 3. Submit for Review (Governance)
            payload = {"brd": brd, "original_prompt": prompt, "cwd": cwd}
            await self.send_message(
                topic="requirements/draft",
                payload=payload,
                is_action=True,
                trace_id=message.id
            )

        elif message.topic == "requirements/verified":
            logger.info(f"Sutra: Requirements verified! Publishing project_spec.json")

            cwd = message.payload.get("cwd", os.getcwd()) if isinstance(message.payload, dict) else os.getcwd()
            spec_content = message.payload.get("brd", message.payload)
            if isinstance(spec_content, dict):
                spec_content = json.dumps(spec_content, indent=2)

            self.write_project_file("project_spec.json", spec_content, project_dir=cwd)

            await self.send_message(
                topic="architecture/input",
                payload=message.payload,
                trace_id=message.trace_id
            )


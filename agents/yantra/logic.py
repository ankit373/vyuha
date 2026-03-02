import re
import os
from core.agent_base import BaseAgent
from core.bus import Message
from typing import List
from core.logger import logger
from core.disk import disk_service

class Yantra(BaseAgent):
    def get_topics(self) -> List[str]:
        return ["development/input", "development/verified"]

    async def handle_message(self, message: Message):
        if message.topic == "development/input":
            logger.info(f"Yantra: Starting code generation for blueprint...")

            cwd = message.payload.get("cwd", os.getcwd()) if isinstance(message.payload, dict) else os.getcwd()
            blueprint = message.payload.get("blueprint", message.payload) if isinstance(message.payload, dict) else message.payload

            # 0. Scan existing project context
            logger.info(f"Yantra: Scanning existing project files in {cwd}...")
            context = disk_service.scan_project_context(cwd)
            file_tree = context["file_tree"]
            file_contents = context["file_contents"]

            existing_context_str = ""
            if file_tree:
                tree_str = "\n".join(f"  - {f}" for f in file_tree[:60])
                existing_context_str = f"\n\n**EXISTING PROJECT FILES (do NOT recreate unless necessary):**\n{tree_str}\n"
                if file_contents:
                    existing_context_str += "\n**EXISTING FILE CONTENTS:**\n"
                    for path, content in list(file_contents.items())[:10]:
                        existing_context_str += f"\n### {path}\n```\n{content[:800]}\n```\n"
                existing_context_str += "\nOnly generate files that are NEW or need to be MODIFIED per the blueprint. Extend existing code, do not start from scratch."

            # 1. Implementation
            code_prompt = (
                "Act as a Lead Software Engineer. Implement this high-fidelity architecture blueprint with production-ready, highly optimized code. "
                "For EACH file mentioned in the blueprint, provide a complete code block. "
                "IMPORTANT: Start each code block with a comment like '# FILE: path/to/file.ext' so I can parse it. "
                "The paths should be relative to the project root (e.g., 'backend/main.py' or 'frontend/package.json'). "
                f"Blueprint: {blueprint}."
                f"{existing_context_str}"
            )
            source_code = await self.ask_ai(code_prompt)

            # 2. Submit for Review
            payload = {"source_code": source_code, "cwd": cwd}
            await self.send_message(
                topic="development/draft",
                payload=payload,
                is_action=True,
                trace_id=message.trace_id
            )

        elif message.topic == "development/verified":
            logger.info(f"Yantra: Code verified! Writing files to disk...")
            source_code = message.payload.get("source_code", "") if isinstance(message.payload, dict) else ""
            cwd = message.payload.get("cwd", os.getcwd()) if isinstance(message.payload, dict) else os.getcwd()

            project_dir = cwd

            # Simple parser for '# FILE: path/to/file' pattern
            files = re.split(r'# FILE: ', source_code)
            for file_block in files[1:]:  # Skip first empty split
                try:
                    lines = file_block.strip().split('\n')
                    filepath = lines[0].strip()
                    # Remove markdown code fences if present
                    content = '\n'.join(lines[1:]).strip()
                    content = re.sub(r'^```[a-z]*\n', '', content)
                    content = re.sub(r'\n```$', '', content)

                    full_path = os.path.join(project_dir, filepath)
                    # ensure directory exists
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)

                    disk_service.write_file(full_path, content)
                    self.render(f"Generated file: [bold cyan]{full_path}[/bold cyan]")
                except Exception as e:
                    logger.error(f"Yantra: Failed to parse/write file block: {e}")

            await self.send_message(
                topic="testing/input",
                payload=message.payload,
                trace_id=message.trace_id
            )


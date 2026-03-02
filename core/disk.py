import os
from core.logger import logger

# File extensions we care about reading for context
READABLE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json",
    ".yaml", ".yml", ".md", ".txt", ".sh", ".env", ".toml", ".xml",
    ".sql", ".go", ".rs", ".java", ".rb", ".php", ".swift", ".kt",
}

# Directories to always skip
IGNORED_DIRS = {
    ".git", "__pycache__", "node_modules", "venv", ".venv", "env",
    ".env", "dist", "build", ".next", ".cache", "coverage", ".pytest_cache",
    "vyuha.log",
}

class DiskService:
    @staticmethod
    def write_file(filename: str, content: str):
        """Write content to a file, creating directories if needed."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
            with open(filename, "w") as f:
                f.write(content)
            logger.info(f"DiskService: Successfully wrote {filename}")
            return True
        except Exception as e:
            logger.error(f"DiskService: Failed to write {filename}: {e}")
            return False

    @staticmethod
    def list_files(directory: str = "."):
        """List files in the specified directory."""
        try:
            return os.listdir(directory)
        except Exception as e:
            logger.error(f"DiskService: Failed to list directory {directory}: {e}")
            return []

    @staticmethod
    def scan_project_context(directory: str = ".", max_files: int = 30, max_file_size_kb: int = 50) -> dict:
        """
        Scan the project directory recursively and return:
          - file_tree: list of relative paths of all discovered files
          - file_contents: dict of {relative_path: content} for readable source files
        Skips ignored dirs and binary/large files.
        """
        file_tree = []
        file_contents = {}
        max_bytes = max_file_size_kb * 1024

        try:
            for root, dirs, files in os.walk(directory):
                # Prune ignored directories in-place
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]

                for fname in files:
                    abs_path = os.path.join(root, fname)
                    rel_path = os.path.relpath(abs_path, directory)
                    file_tree.append(rel_path)

                    # Only read files within readable extensions and size limit
                    _, ext = os.path.splitext(fname)
                    if ext.lower() in READABLE_EXTENSIONS and len(file_contents) < max_files:
                        try:
                            size = os.path.getsize(abs_path)
                            if size <= max_bytes:
                                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                                    file_contents[rel_path] = f.read()
                        except Exception as e:
                            logger.debug(f"DiskService: Could not read {rel_path}: {e}")

        except Exception as e:
            logger.error(f"DiskService: Failed to scan directory {directory}: {e}")

        logger.info(f"DiskService: Scanned {len(file_tree)} files in '{directory}', read {len(file_contents)} source files.")
        return {"file_tree": file_tree, "file_contents": file_contents}

disk_service = DiskService()


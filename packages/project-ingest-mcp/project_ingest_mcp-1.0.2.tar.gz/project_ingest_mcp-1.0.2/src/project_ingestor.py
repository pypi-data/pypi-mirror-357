import re
import asyncio
from gitingest import ingest
from typing import Any, Dict, Optional


class ProjectIngestor:
    def __init__(self, project: str):
        """Initialize the ProjectIngestor with a project directory."""
        self.project: str = project
        self.summary: Optional[Dict[str, Any]] = None
        self.tree: Optional[Any] = None

        self.raw_content: Optional[str] = None
        self.content: Optional[Dict[str, str]] = None

    async def analysis_project(self) -> None:
        """Asynchronously analysis project data."""
        # Run the synchronous ingest function in a thread pool
        loop = asyncio.get_event_loop()
        raw_summary, self.tree, self.raw_content = await loop.run_in_executor(None, lambda: ingest(self.project))

        self.parse_summary(raw_summary)
        self.parse_content()

    def parse_summary(self, raw_summary: str):
        """Parse the summary string into a structured dictionary."""
        self.summary = {}

        try:
            # Extract repository name
            repo_match = re.search(r"(?:Repository|Project|Directory): (.+)", raw_summary)
            if repo_match:
                self.summary["project"] = repo_match.group(1).strip()
            else:
                self.summary["project"] = ""

            # Extract files analyzed
            files_match = re.search(r"Files analyzed: (\d+)", raw_summary)
            if files_match:
                self.summary["num_files"] = int(files_match.group(1))
            else:
                self.summary["num_files"] = None

            # Extract estimated tokens
            tokens_match = re.search(r"Estimated tokens: (.+)", raw_summary)
            if tokens_match:
                self.summary["token_count"] = tokens_match.group(1).strip()
            else:
                self.summary["token_count"] = ""

        except Exception:
            # If any regex operation fails, set default values
            self.summary["project"] = ""
            self.summary["num_files"] = None
            self.summary["token_count"] = ""

        # Store the original string as well
        self.summary["raw"] = raw_summary

    def parse_content(self):
        """Parse the content string into a structured dictionary."""
        self.content = {}

        lines = self.raw_content.split("\n")

        seperator = "=" * 48

        current_file_name = None
        current_file_content = []

        for line in lines:
            if line == seperator:
                if current_file_name and current_file_content:
                    self.content[current_file_name] = "\n".join(current_file_content).strip()
                    current_file_name = None
                    current_file_content = []
                continue

            file_name_match = re.search(r"File: (.*)", line.strip())

            if not current_file_content and file_name_match:
                current_file_name = file_name_match.group(1).strip()
                continue

            current_file_content.append(line)


        # The last one file
        self.content[current_file_name] = "\n".join(current_file_content).strip()


    def get_summary(self) -> Dict[str, Any]:
        """Returns the project summary."""
        return self.summary

    def get_tree(self) -> Any:
        """Returns the project tree structure."""
        return self.tree

    def get_content(self, file_path: str = None) -> str:
        """Returns the repository content."""
        if file_path is None:
            return self.raw_content

        return self.content[file_path]



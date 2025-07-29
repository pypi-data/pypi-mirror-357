import asyncio
from typing import Dict

from fastmcp import FastMCP, Client

from src.project_ingestor import ProjectIngestor

mcp = FastMCP("project-ingest-mcp")


@mcp.tool()
async def project_summary(
        project: str
) -> Dict[str, any]:
    """
    Get a summary of a project that includes
        - project name,
        - Files in project
        - Number of tokens in repo
        - Summary from the README.md

    Args:
        project: The path of the project
    """

    ingestor = ProjectIngestor(project)
    await ingestor.analysis_project()
    return ingestor.get_summary()

@mcp.tool()
async def project_tree(project: str) -> str:
    """
    Get the tree structure of a project

    Args:
        project: The path of the project
    """
    ingestor = ProjectIngestor(project)
    await ingestor.analysis_project()
    return ingestor.get_tree()


@mcp.tool()
async def file_content(project: str, file_path: str = None) -> str:
    """
    Get the content of specific files from a project

    Args:
        project: The path of project
        file_path: path to file within the project
    """

    ingestor = ProjectIngestor(project)
    await ingestor.analysis_project()

    return ingestor.get_content(file_path)

def main():
  """Entry point for the project-ingest-mcp command."""
  mcp.run(transport='stdio')

if __name__ == "__main__":
    # Initialize and run the server
    main()

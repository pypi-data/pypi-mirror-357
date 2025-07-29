import asyncio


from src.project_ingestor import ProjectIngestor


async def print_project_ingest_info(name: str):
    ingestor = ProjectIngestor(name)

    await ingestor.analysis_project()

    print(ingestor.get_tree())

    print(ingestor.get_summary())

    print(ingestor.get_content())

asyncio.run(print_project_ingest_info("/Users/linyimin/PycharmProjects/project-ingest-mcp"))
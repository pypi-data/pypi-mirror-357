from typing import List

from mcp.types import Resource

TABLE_RESOURCE = Resource(
    uri="openmetadata://table",
    name="Table",
    description="A table in the database",
)


def list_all_resources() -> List[Resource]:
    return [TABLE_RESOURCE]

from typing import Any, Dict, List

from mcp.types import TextContent, Tool

from src.openmetadata import OpenMetadataClient

LIST_TABLES_TOOL = Tool(
    name="list_tables",
    description="List tables from OpenMetadata",
    inputSchema={
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Maximum number of tables to return", "default": 10},
            "offset": {"type": "integer", "description": "Number of tables to skip", "default": 0},
        },
    },
)

GET_TABLE_TOOL = Tool(
    name="get_table",
    description="Get details of a specific table by ID",
    inputSchema={
        "type": "object",
        "properties": {
            "table_id": {"type": "string", "description": "ID of the table to retrieve", "format": "uuid"},
            "fields": {
                "type": "string",
                "description": "Fields to include in the response",
                "example": "name,description,columns,tags,href",
            },
        },
        "required": ["table_id"],
    },
)

GET_TABLE_BY_NAME_TOOL = Tool(
    name="get_table_by_name",
    description="Get details of a specific table by fully qualified name",
    inputSchema={
        "type": "object",
        "properties": {
            "fqn": {"type": "string", "description": "Fully qualified name of the table"},
            "fields": {
                "type": "string",
                "description": "Fields to include in the response",
                "example": "name,description,columns,tags,href",
            },
        },
        "required": ["fqn"],
    },
)

CREATE_TABLE_TOOL = Tool(
    name="create_table",
    description="Create a new table",
    inputSchema={
        "type": "object",
        "properties": {
            "table_data": {"type": "object", "description": "Table data including name, description, columns, etc."},
        },
        "required": ["table_data"],
    },
)

UPDATE_TABLE_TOOL = Tool(
    name="update_table",
    description="Update an existing table",
    inputSchema={
        "type": "object",
        "properties": {
            "table_id": {"type": "string", "description": "ID of the table to update", "format": "uuid"},
            "table_data": {"type": "object", "description": "Updated table data"},
        },
        "required": ["table_id", "table_data"],
    },
)

DELETE_TABLE_TOOL = Tool(
    name="delete_table",
    description="Delete a table",
    inputSchema={
        "type": "object",
        "properties": {
            "table_id": {"type": "string", "description": "ID of the table to delete", "format": "uuid"},
            "hard_delete": {"type": "boolean", "description": "Whether to perform a hard delete", "default": False},
            "recursive": {"type": "boolean", "description": "Whether to recursively delete children", "default": False},
        },
        "required": ["table_id"],
    },
)


def list_all_tools() -> List[Tool]:
    return [
        LIST_TABLES_TOOL,
        GET_TABLE_TOOL,
        GET_TABLE_BY_NAME_TOOL,
        CREATE_TABLE_TOOL,
        UPDATE_TABLE_TOOL,
        DELETE_TABLE_TOOL,
    ]


def call_tool(name: str, arguments: Dict[str, Any], client: OpenMetadataClient) -> List[TextContent]:
    if name == LIST_TABLES_TOOL.name:
        limit = arguments.get("limit", 10)
        offset = arguments.get("offset", 0)
        results = client.list_tables(limit=limit, offset=offset)
        return [TextContent(type="text", text=str(results))]
    elif name == GET_TABLE_TOOL.name:
        table_id = arguments["table_id"]
        fields = arguments.get("fields")
        results = client.get_table(table_id=table_id, fields=fields)
        return [TextContent(type="text", text=str(results))]
    elif name == GET_TABLE_BY_NAME_TOOL.name:
        fqn = arguments["fqn"]
        fields = arguments.get("fields")
        results = client.get_table_by_name(fqn=fqn, fields=fields)
        return [TextContent(type="text", text=str(results))]
    elif name == CREATE_TABLE_TOOL.name:
        table_data = arguments["table_data"]
        results = client.create_table(table_data=table_data)
        return [TextContent(type="text", text=str(results))]
    elif name == UPDATE_TABLE_TOOL.name:
        table_id = arguments["table_id"]
        table_data = arguments["table_data"]
        results = client.update_table(table_id=table_id, table_data=table_data)
        return [TextContent(type="text", text=str(results))]
    elif name == DELETE_TABLE_TOOL.name:
        table_id = arguments["table_id"]
        hard_delete = arguments.get("hard_delete", False)
        recursive = arguments.get("recursive", False)
        client.delete_table(table_id=table_id, hard_delete=hard_delete, recursive=recursive)
        return [TextContent(type="text", text=f"Table {table_id} deleted successfully")]
    else:
        raise ValueError(f"Unknown tool: {name}")

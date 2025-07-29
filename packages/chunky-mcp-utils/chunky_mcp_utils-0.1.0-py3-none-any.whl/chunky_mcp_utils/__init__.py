import uuid
import json
from . import chunker
from mcp import types

def handle_large_response(response_data, tool_name, chunker):
    if chunker.is_response_too_large(response_data):
        unique_hash = str(uuid.uuid4())[:8]
        chunk_info = chunker.save_large_response(response_data, tool_name, unique_hash)
        return [types.TextContent(
            type="text",
            text=json.dumps(chunk_info, indent=2)
        )]
    return response_data
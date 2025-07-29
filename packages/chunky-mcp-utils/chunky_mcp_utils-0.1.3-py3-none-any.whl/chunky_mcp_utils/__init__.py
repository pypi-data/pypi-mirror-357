import uuid
from . import chunker

def handle_large_response(response_data, tool_name):
    _chunker = chunker.ResponseChunker()
    if _chunker.is_response_too_large(response_data):
        unique_hash = str(uuid.uuid4())[:8]
        chunk_info = _chunker.save_large_response(response_data, tool_name, unique_hash)
        return chunk_info
    return response_data
import json
import hashlib
import tempfile
import os

class ResponseChunker:
    def __init__(self):
        self.MAX_RESPONSE_SIZE = 50000
        self.MAX_CHUNK_SIZE = 30000

    def is_response_too_large(self, response_data):
        return len(json.dumps(response_data)) > self.MAX_RESPONSE_SIZE

    def save_large_response(self, response_data, tool_name, params_hash):
        """Save large response to temporary file and return metadata"""
        response_json = json.dumps(response_data, indent=2)
        
        # Create unique filename
        file_id = f"{tool_name}_{params_hash}_{hashlib.md5(response_json.encode()).hexdigest()[:8]}"
        temp_file = os.path.join(tempfile.gettempdir(), f"mcp_response_{file_id}.json")
        
        with open(temp_file, 'w') as f:
            f.write(response_json)
        
        return {
            'type': 'large_response',
            'file_path': temp_file,
            'total_size': len(response_json),
            'message': f"MAKE SURE TO READ ALL CHUNKS!. Response too large ({len(response_json)} chars). Use read_response_chunk tool with file_path '{temp_file}' to read in ALL chunks. \
                Total chunks available: {(len(response_json) + self.MAX_CHUNK_SIZE - 1) // self.MAX_CHUNK_SIZE}. Be sure to read all chunks to get the full response."
        }
# chunky-mcp-utils

Utilities for handling large responses in chunky-mcp tools.

## Installation

```bash
pip install chunky-mcp-utils
```

## Usage

Import the helper in your tool:

```python
from chunky_mcp_utils import handle_large_response

@mcp.tool()
def my_tool() -> list[types.TextContent]:
    """
    Gets a list of all the employees in the system from the database
    """
    # Might give a large JSON response
    response = requests.get("https://someblob.com")
    response.raise_for_status()
    response_data = response.json()
    
    # Chunker hanldes the large response and calls following read chunk tools
    result = handle_large_response(response_data, "my_tool", chunker)
```

## License

MIT
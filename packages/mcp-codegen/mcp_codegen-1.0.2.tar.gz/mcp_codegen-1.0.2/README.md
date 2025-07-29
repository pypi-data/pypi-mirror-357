# MCP CodeGen

MCP CodeGen is a powerful code generation tool designed to create Model Context Protocol (MCP) server implementations from YAML specifications. This tool automates the process of creating structured MCP tools and server code, making it easier to maintain and scale MCP-based applications.

## Overview

MCP CodeGen takes a YAML configuration file (`mcp_cfg.yaml`) that defines MCP tools and their specifications, and generates:
- Individual tool implementation files
- MCP server configuration
- Required project structure

## YAML Specification Format

The YAML configuration should follow this structure:

```yaml
mcp_server:
  mcp_transport_mode: "sse" ##  it can be stdio, sse or streamable-http
  mcp_tools:
    - tool_name: <tool name>
      tool_description: <tool description>
      tool_args:
        - arg_variable: <argument variable name>
          arg_type: <data type>
          arg_description: <argument description>
```

### Example Configuration

```yaml
mcp_server:
  mcp_transport_mode: "sse"
  mcp_tools:
    - tool_name: add
      tool_description: "sum of two numbers"
      tool_args:
        - arg_variable: "num_a"
          arg_type: int
          arg_description: "first number"
        - arg_variable: "num_b"
          arg_type: int
          arg_description: "2nd number"
```

## Generated Project Structure

The tool generates the following project structure:

```
project_root/
├── tools/                  # Directory containing tool implementations
│   └── <tool_name>_tool.py
├── mcp_server.py          # MCP server configuration
├── requirements.txt       # Project dependencies
└── mcp_cfg.yaml          # Tool configuration file
```

### Generated Files

1. **Tool Implementation Files** (`tools/<tool_name>_tool.py`):
   - Auto-generated tool modules with proper typing and documentation
   - Function signatures based on YAML specifications
   - Docstrings with descriptions and parameter documentation

2. **MCP Server** (`mcp_server.py`):
   - FastMCP server configuration
   - Automatic tool registration
   - Proper imports of all tool modules

## Usage

1. Create your `mcp_cfg.yaml` file in the project root directory with your tool specifications following the format shown above
2. Install the package:
   ```bash
   pip install pyyaml mcp-codegen
   ```
3. Run the code generator in your project directory (where mcp_cfg.yaml is located):
   ```bash
   mcp-proj-build
   ```
4. The tool will:
   - Validate your YAML configuration
   - Create the project structure
   - Generate tool implementation files
   - Create the MCP server configuration

5. Implement the tool logic in the generated tool files
6. Run your MCP server

## Requirements

The project requires:
- Python 3.9+
- pyyaml
- MCP

mcp-codegen will create requirements.txt with required dependencies.

## Generated Code Examples

### Tool Implementation Example

```python
def add(num_a: int, num_b: int) -> Any:
    """
    sum of two numbers

    Parameters
    ----------
    num_a (int): first number
    num_b (int): second number

    Returns
    -------
    Any
        Result of the tool.
    """
    # TODO: implement tool logic
    raise NotImplementedError  # Replace with you custom logic
```

### MCP Server Configuration Example

```python
from tools import add_tool
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")

# Register tools
mcp.add_tool(add_tool.add)
```

# Error Repository MCP Server

An MCP (Model Context Protocol) server that provides access to an error database stored in Excel format. This server can answer questions about error codes, descriptions, and provide probable solutions for various types of technical errors.

## Features

- **Error Code Lookup**: Search for specific errors by their error codes (e.g., E001, DB001, NET001)
- **Description Search**: Find errors by searching through error descriptions and types
- **Category Filtering**: Browse errors by categories (Programming, Database, Network, Security, System)
- **Error Summary**: Get statistics and overview of the error database
- **Excel Database**: Easily maintainable error repository in Excel format

## Error Database

The server includes a comprehensive error database with:

- **Programming Errors**: Syntax errors, reference errors, type errors
- **Database Errors**: Connection issues, SQL syntax problems, schema errors  
- **Network Errors**: Timeouts, HTTP errors, connectivity issues
- **Security Errors**: Authentication and authorization problems
- **System Errors**: Memory issues, disk space problems

Each error entry includes:
- Error code (unique identifier)
- Error type and description
- Severity level
- Category
- Detailed solution steps
- Code examples
- Related error references

## Installation

### From PyPI (Recommended)
```bash
pip install error-repository-server
```

### From Source
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/error-repository-server.git
   cd error-repository-server
   ```
2. Install dependencies:
   ```bash
   pip install -e .
   ```

## Usage

### Running the Server

To run the MCP server directly:
```bash
python -m error_repository_server.server
```

### Configuration for MCP Clients

Add this to your MCP client configuration:

**For Claude Desktop:**
```json
{
  "mcpServers": {
    "error-repository": {
      "command": "python",
      "args": ["-m", "error_repository_server.server"]
    }
  }
}
```

**For other MCP clients:**
```json
{
  "name": "error-repository-server",
  "command": "python",
  "args": ["-m", "error_repository_server.server"],
  "env": {}
}
```

### Available Tools

The server provides the following tools:

1. **search_error_by_code**: Find a specific error by its code
   - Input: `error_code` (string)
   - Example: "E001", "DB001", "NET001"

2. **search_error_by_description**: Search errors by keywords
   - Input: `description` (string)  
   - Example: "timeout", "syntax", "connection"

3. **search_error_by_category**: Filter errors by category
   - Input: `category` (string)
   - Example: "Programming", "Database", "Network"

4. **get_error_categories**: List all available categories

5. **get_error_summary**: Get database statistics and overview

### Integration with GitHub Copilot

This MCP server is designed to integrate with GitHub Copilot. The `.vscode/mcp.json` configuration file enables VS Code to use this server as a context provider.

To use with GitHub Copilot:
1. Ensure the server is configured in `.vscode/mcp.json`
2. The server will be available as a context source for Copilot
3. Ask Copilot questions about error codes or problems, and it can query this server for solutions

### Example Queries

- "What is error code E001?"
- "How do I fix a syntax error?"
- "Show me all database errors"
- "What are the available error categories?"
- "Give me a summary of the error database"

## Customizing the Error Database

To add or modify errors:

1. Edit the `create_error_db.py` file
2. Add new error entries to the `error_data` list
3. Run the script to regenerate the Excel file:
   ```bash
   python create_error_db.py
   ```

## Error Database Schema

Each error record contains:
- `error_code`: Unique identifier (e.g., "E001")
- `error_type`: Type of error (e.g., "Syntax Error")
- `error_description`: Brief description of the error
- `severity`: Error severity (Critical, High, Medium, Low)
- `category`: Error category (Programming, Database, etc.)
- `solution`: Detailed solution steps
- `example`: Code examples or additional help
- `related_errors`: Comma-separated list of related error codes

## Development

The server is built using:
- **MCP SDK**: For Model Context Protocol implementation
- **pandas**: For Excel data processing
- **openpyxl**: For Excel file handling
- **pydantic**: For data validation

## License

MIT License - see LICENSE file for details.

## Support

For issues or questions about this MCP server, please refer to the MCP documentation: https://github.com/modelcontextprotocol/create-python-server

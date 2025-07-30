"""
Error Repository MCP Server

This server provides access to an error database stored in Excel format.
It can answer questions about error codes, descriptions, and provide solutions.
"""

import asyncio
import logging
from typing import Any, Sequence
import pandas as pd
import os
from pathlib import Path

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("error-repository-server")

class ErrorRepository:
    """Handles loading and querying the error database"""
    
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.df = None
        self.load_database()
    
    def load_database(self):
        """Load the error database from Excel file"""
        try:
            if os.path.exists(self.excel_path):
                self.df = pd.read_excel(self.excel_path, sheet_name='ErrorRepository')
                logger.info(f"Loaded error database with {len(self.df)} records")
            else:
                logger.error(f"Error database file not found: {self.excel_path}")
                self.df = pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to load error database: {e}")
            self.df = pd.DataFrame()
    
    def search_by_error_code(self, error_code: str) -> dict:
        """Search for error by exact error code"""
        if self.df is None or self.df.empty:
            return {"error": "Error database not available"}
        
        result = self.df[self.df['error_code'].str.upper() == error_code.upper()]
        if not result.empty:
            record = result.iloc[0]
            return {
                "error_code": record['error_code'],
                "error_type": record['error_type'], 
                "description": record['error_description'],
                "severity": record['severity'],
                "category": record['category'],
                "solution": record['solution'],
                "example": record['example'],
                "related_errors": record['related_errors']
            }
        return {"error": f"Error code '{error_code}' not found in database"}
    
    def search_by_description(self, description: str) -> list:
        """Search for errors by description keywords"""
        if self.df is None or self.df.empty:
            return [{"error": "Error database not available"}]
        
        # Case-insensitive search in description and error_type columns
        mask = (
            self.df['error_description'].str.contains(description, case=False, na=False) |
            self.df['error_type'].str.contains(description, case=False, na=False)
        )
        results = self.df[mask]
        
        if not results.empty:
            return [
                {
                    "error_code": row['error_code'],
                    "error_type": row['error_type'],
                    "description": row['error_description'], 
                    "severity": row['severity'],
                    "category": row['category'],
                    "solution": row['solution'],
                    "example": row['example'],
                    "related_errors": row['related_errors']
                }
                for _, row in results.iterrows()
            ]
        return [{"error": f"No errors found matching description: '{description}'"}]
    
    def search_by_category(self, category: str) -> list:
        """Search for errors by category"""
        if self.df is None or self.df.empty:
            return [{"error": "Error database not available"}]
        
        results = self.df[self.df['category'].str.contains(category, case=False, na=False)]
        
        if not results.empty:
            return [
                {
                    "error_code": row['error_code'],
                    "error_type": row['error_type'],
                    "description": row['error_description'],
                    "severity": row['severity'], 
                    "category": row['category'],
                    "solution": row['solution'],
                    "example": row['example'],
                    "related_errors": row['related_errors']
                }
                for _, row in results.iterrows()
            ]
        return [{"error": f"No errors found in category: '{category}'"}]
    
    def get_all_categories(self) -> list:
        """Get all available error categories"""
        if self.df is None or self.df.empty:
            return []
        return self.df['category'].unique().tolist()
    
    def get_error_summary(self) -> dict:
        """Get summary statistics of the error database"""
        if self.df is None or self.df.empty:
            return {"error": "Error database not available"}
        
        return {
            "total_errors": len(self.df),
            "categories": self.df['category'].unique().tolist(),
            "severity_counts": self.df['severity'].value_counts().to_dict(),
            "error_types": self.df['error_type'].unique().tolist()
        }

# Initialize the error repository
current_dir = Path(__file__).parent
excel_path = current_dir.parent.parent / "error_database.xlsx"
error_repo = ErrorRepository(str(excel_path))

# Create the MCP server
server = Server("error-repository-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for the MCP server"""
    return [
        types.Tool(
            name="search_error_by_code",
            description="Search for a specific error by its error code (e.g., E001, DB001)",
            inputSchema={
                "type": "object",
                "properties": {
                    "error_code": {
                        "type": "string",
                        "description": "The error code to search for (e.g., E001, DB001, NET001)"
                    }
                },
                "required": ["error_code"]
            }
        ),
        types.Tool(
            name="search_error_by_description", 
            description="Search for errors by description keywords or error type",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string", 
                        "description": "Keywords to search in error descriptions or types"
                    }
                },
                "required": ["description"]
            }
        ),
        types.Tool(
            name="search_error_by_category",
            description="Search for errors by category (Programming, Database, Network, Security, System)",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The error category to search for"
                    }
                },
                "required": ["category"]
            }
        ),
        types.Tool(
            name="get_error_categories",
            description="Get all available error categories in the database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_error_summary",
            description="Get summary statistics of the error database",
            inputSchema={
                "type": "object", 
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent]:
    """Handle tool calls from the MCP client"""
    
    if name == "search_error_by_code":
        error_code = arguments.get("error_code") if arguments else None
        if not error_code:
            return [types.TextContent(
                type="text",
                text="Error: error_code parameter is required"
            )]
        
        result = error_repo.search_by_error_code(error_code)
        
        if "error" in result:
            return [types.TextContent(type="text", text=result["error"])]
        
        response = f"""**Error Code:** {result['error_code']}
**Type:** {result['error_type']}
**Description:** {result['description']}
**Severity:** {result['severity']}
**Category:** {result['category']}

**Solution:**
{result['solution']}

**Example:**
{result['example']}

**Related Errors:** {result['related_errors']}"""
        
        return [types.TextContent(type="text", text=response)]
    
    elif name == "search_error_by_description":
        description = arguments.get("description") if arguments else None
        if not description:
            return [types.TextContent(
                type="text",
                text="Error: description parameter is required"
            )]
        
        results = error_repo.search_by_description(description)
        
        if len(results) == 1 and "error" in results[0]:
            return [types.TextContent(type="text", text=results[0]["error"])]
        
        response = f"Found {len(results)} error(s) matching '{description}':\n\n"
        for i, result in enumerate(results, 1):
            response += f"**{i}. Error Code:** {result['error_code']}\n"
            response += f"**Type:** {result['error_type']}\n"
            response += f"**Description:** {result['description']}\n"
            response += f"**Solution:** {result['solution']}\n\n"
        
        return [types.TextContent(type="text", text=response)]
    
    elif name == "search_error_by_category":
        category = arguments.get("category") if arguments else None
        if not category:
            return [types.TextContent(
                type="text",
                text="Error: category parameter is required"
            )]
        
        results = error_repo.search_by_category(category)
        
        if len(results) == 1 and "error" in results[0]:
            return [types.TextContent(type="text", text=results[0]["error"])]
        
        response = f"Found {len(results)} error(s) in category '{category}':\n\n"
        for i, result in enumerate(results, 1):
            response += f"**{i}. {result['error_code']}:** {result['error_type']}\n"
            response += f"   {result['description']}\n\n"
        
        return [types.TextContent(type="text", text=response)]
    
    elif name == "get_error_categories":
        categories = error_repo.get_all_categories()
        response = "Available error categories:\n" + "\n".join(f"- {cat}" for cat in categories)
        return [types.TextContent(type="text", text=response)]
    
    elif name == "get_error_summary":
        summary = error_repo.get_error_summary()
        
        if "error" in summary:
            return [types.TextContent(type="text", text=summary["error"])]
        
        response = f"""**Error Database Summary:**

**Total Errors:** {summary['total_errors']}

**Categories:** {', '.join(summary['categories'])}

**Severity Distribution:**
{chr(10).join(f"- {sev}: {count}" for sev, count in summary['severity_counts'].items())}

**Error Types:** {', '.join(summary['error_types'])}"""
        
        return [types.TextContent(type="text", text=response)]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def main():
    """Main entry point for the server"""
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="error-repository-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())

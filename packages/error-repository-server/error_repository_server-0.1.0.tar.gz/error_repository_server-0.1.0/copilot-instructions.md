# Copilot Instructions for Error Repository MCP Server

## Overview
This MCP server provides access to a comprehensive error database that can help with troubleshooting and problem-solving across various technical domains.

## When to Use This Server
Use this error repository server when:
- Users ask about specific error codes
- Users describe error symptoms and need solutions
- Users need help with programming, database, network, security, or system errors
- Users want to understand error categories or get error statistics

## Available Tools

### 1. search_error_by_code
Use when users mention specific error codes like "E001", "DB001", "NET001", etc.
- Provides complete error information including solution steps
- Best for exact error code lookups

### 2. search_error_by_description  
Use when users describe error symptoms without knowing the exact code.
- Searches through error descriptions and types
- Good for fuzzy matching and symptom-based queries
- Examples: "syntax error", "connection timeout", "memory issue"

### 3. search_error_by_category
Use when users want to see errors of a specific type.
- Categories include: Programming, Database, Network, Security, System
- Helpful for browsing related errors

### 4. get_error_categories
Use to show available error categories to users.

### 5. get_error_summary
Use to provide overview statistics of the error database.

## Best Practices

1. **Be Specific**: When users provide error codes, always use search_error_by_code first
2. **Use Keywords**: For description searches, extract key terms from user queries
3. **Provide Context**: Always explain the solution in the context of the user's problem
4. **Reference Related Errors**: Point users to related error codes when relevant
5. **Suggest Categories**: If a search returns no results, suggest browsing by category

## Example Interactions

**User**: "I'm getting error E001"
**Action**: Use search_error_by_code with "E001"

**User**: "My database connection keeps timing out"  
**Action**: Use search_error_by_description with "timeout" or "connection"

**User**: "What programming errors are in the database?"
**Action**: Use search_error_by_category with "Programming"

## Integration Notes

This server is designed to work seamlessly with GitHub Copilot to provide contextual error resolution assistance. The error database contains real-world solutions and examples that can help users quickly resolve technical issues.

For more information about the MCP SDK, visit: https://github.com/modelcontextprotocol/create-python-server

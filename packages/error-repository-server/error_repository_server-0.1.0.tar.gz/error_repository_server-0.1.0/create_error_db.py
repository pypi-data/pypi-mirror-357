import pandas as pd
import os

def create_error_database():
    """Create an Excel file with sample error data"""
    
    # Sample error data with different types of errors
    error_data = [
        {
            "error_code": "E001",
            "error_type": "Syntax Error",
            "error_description": "Missing semicolon at end of statement",
            "severity": "High",
            "category": "Programming",
            "solution": "Add a semicolon (;) at the end of the statement. Check line ending syntax according to your programming language requirements.",
            "example": "Instead of: let x = 5\nUse: let x = 5;",
            "related_errors": "E002, E010"
        },
        {
            "error_code": "E002", 
            "error_type": "Syntax Error",
            "error_description": "Unexpected token or character",
            "severity": "High",
            "category": "Programming",
            "solution": "Remove or replace the unexpected character. Check for typos, wrong brackets, or misplaced operators.",
            "example": "Check for: extra commas, wrong bracket types [], {}, (), misplaced operators",
            "related_errors": "E001, E003"
        },
        {
            "error_code": "E003",
            "error_type": "Reference Error", 
            "error_description": "Variable is not defined",
            "severity": "High",
            "category": "Programming",
            "solution": "Declare the variable before using it, or check for typos in variable names. Ensure proper scoping.",
            "example": "Declare: let variableName = value; before using variableName",
            "related_errors": "E004, E015"
        },
        {
            "error_code": "E004",
            "error_type": "Type Error",
            "error_description": "Cannot read property of undefined",
            "severity": "Medium",
            "category": "Programming", 
            "solution": "Check if the object exists before accessing its properties. Use optional chaining or null checks.",
            "example": "Use: object?.property or if(object) { object.property }",
            "related_errors": "E003, E005"
        },
        {
            "error_code": "E005",
            "error_type": "Type Error",
            "error_description": "Function is not defined",
            "severity": "High",
            "category": "Programming",
            "solution": "Define the function before calling it, import it properly, or check function name spelling.",
            "example": "Define: function myFunction() { ... } before calling myFunction()",
            "related_errors": "E003, E006"
        },
        {
            "error_code": "DB001",
            "error_type": "Database Error",
            "error_description": "Connection timeout to database",
            "severity": "Critical",
            "category": "Database",
            "solution": "Check database server status, network connectivity, increase timeout settings, verify connection string.",
            "example": "Set connection timeout: { timeout: 30000 } or check if database service is running",
            "related_errors": "DB002, DB003"
        },
        {
            "error_code": "DB002",
            "error_type": "Database Error", 
            "error_description": "Invalid SQL syntax",
            "severity": "High",
            "category": "Database",
            "solution": "Review SQL query syntax, check table/column names, verify SQL dialect compatibility.",
            "example": "Common issues: missing quotes around strings, wrong JOIN syntax, typos in keywords",
            "related_errors": "DB001, DB004"
        },
        {
            "error_code": "DB003",
            "error_type": "Database Error",
            "error_description": "Table or column does not exist",
            "severity": "High", 
            "category": "Database",
            "solution": "Verify table/column names exist in database schema, check spelling, ensure proper database selection.",
            "example": "Use: DESCRIBE tablename; or SHOW COLUMNS FROM tablename; to verify structure",
            "related_errors": "DB002, DB005"
        },
        {
            "error_code": "NET001",
            "error_type": "Network Error",
            "error_description": "Request timeout",
            "severity": "Medium",
            "category": "Network",
            "solution": "Increase timeout duration, check network connection, verify server availability, implement retry logic.",
            "example": "Set timeout: fetch(url, { timeout: 10000 }) or add retry mechanism",
            "related_errors": "NET002, NET003"
        },
        {
            "error_code": "NET002",
            "error_type": "Network Error",
            "error_description": "404 Not Found",
            "severity": "Medium",
            "category": "Network", 
            "solution": "Verify URL correctness, check if resource exists, validate API endpoint, check routing configuration.",
            "example": "Verify: protocol (http/https), domain name, path, query parameters",
            "related_errors": "NET001, NET004"
        },
        {
            "error_code": "NET003",
            "error_type": "Network Error",
            "error_description": "500 Internal Server Error",
            "severity": "Critical",
            "category": "Network",
            "solution": "Check server logs, verify server configuration, check database connectivity, review application code.",
            "example": "Check: server error logs, database connections, memory usage, disk space",
            "related_errors": "NET002, DB001"
        },
        {
            "error_code": "AUTH001", 
            "error_type": "Authentication Error",
            "error_description": "Invalid credentials",
            "severity": "High",
            "category": "Security",
            "solution": "Verify username/password, check account status, reset credentials if needed, validate authentication method.",
            "example": "Check: correct username, password not expired, account not locked, proper hash comparison",
            "related_errors": "AUTH002, AUTH003"
        },
        {
            "error_code": "AUTH002",
            "error_type": "Authorization Error", 
            "error_description": "Access denied - insufficient permissions",
            "severity": "High",
            "category": "Security",
            "solution": "Grant required permissions, check user roles, verify access control lists, contact administrator.",
            "example": "Required: READ, WRITE, ADMIN permissions for specific resources",
            "related_errors": "AUTH001, AUTH003"
        },
        {
            "error_code": "SYS001",
            "error_type": "System Error",
            "error_description": "Out of memory",
            "severity": "Critical", 
            "category": "System",
            "solution": "Increase memory allocation, optimize memory usage, check for memory leaks, restart application.",
            "example": "Monitor: heap size, garbage collection, memory-intensive operations",
            "related_errors": "SYS002, SYS003"
        },
        {
            "error_code": "SYS002",
            "error_type": "System Error",
            "error_description": "Disk space full",
            "severity": "Critical",
            "category": "System", 
            "solution": "Free up disk space, move files to other drives, increase storage capacity, clean temporary files.",
            "example": "Clean: logs, cache, temporary files, old backups",
            "related_errors": "SYS001, SYS003"
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(error_data)
    
    # Create the Excel file
    excel_path = os.path.join(os.path.dirname(__file__), "error_database.xlsx")
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='ErrorRepository', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['ErrorRepository']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"Error database created at: {excel_path}")
    return excel_path

if __name__ == "__main__":
    create_error_database()

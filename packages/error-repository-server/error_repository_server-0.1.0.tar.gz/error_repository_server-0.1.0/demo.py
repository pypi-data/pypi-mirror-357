"""
Demo script to showcase the Error Repository MCP Server functionality
"""

import asyncio
import json
from error_repository_server.server import error_repo

async def demo_server_functionality():
    """Demonstrate the server's capabilities"""
    print("🔍 Error Repository MCP Server Demo")
    print("=" * 50)
    
    # Test 1: Search by error code
    print("\n1. Searching for error code 'E001':")
    result = error_repo.search_by_error_code("E001")
    if "error" not in result:
        print(f"   ✅ Found: {result['error_type']}")
        print(f"   📝 Description: {result['description']}")
        print(f"   💡 Solution: {result['solution'][:100]}...")
    else:
        print(f"   ❌ {result['error']}")
    
    # Test 2: Search by description
    print("\n2. Searching for 'timeout' errors:")
    results = error_repo.search_by_description("timeout")
    if results and "error" not in results[0]:
        print(f"   ✅ Found {len(results)} matching error(s):")
        for r in results[:2]:  # Show first 2
            print(f"   - {r['error_code']}: {r['description']}")
    else:
        print(f"   ❌ {results[0]['error'] if results else 'No results'}")
    
    # Test 3: Search by category
    print("\n3. Searching for 'Database' category:")
    results = error_repo.search_by_category("Database")
    if results and "error" not in results[0]:
        print(f"   ✅ Found {len(results)} database error(s):")
        for r in results[:3]:  # Show first 3
            print(f"   - {r['error_code']}: {r['error_type']}")
    else:
        print(f"   ❌ {results[0]['error'] if results else 'No results'}")
    
    # Test 4: Get categories
    print("\n4. Available categories:")
    categories = error_repo.get_all_categories()
    if categories:
        print(f"   ✅ Categories: {', '.join(categories)}")
    else:
        print("   ❌ No categories found")
    
    # Test 5: Get summary
    print("\n5. Database summary:")
    summary = error_repo.get_error_summary()
    if "error" not in summary:
        print(f"   ✅ Total errors: {summary['total_errors']}")
        print(f"   📊 Severity distribution: {summary['severity_counts']}")
    else:
        print(f"   ❌ {summary['error']}")
    
    print("\n🎉 Demo completed! The MCP server is ready for GitHub Copilot integration.")
    print("\nExample questions you can ask GitHub Copilot:")
    print("- 'What is error code E001?'")
    print("- 'How do I fix a database connection timeout?'")
    print("- 'Show me all programming errors'")
    print("- 'What are the available error categories?'")

if __name__ == "__main__":
    asyncio.run(demo_server_functionality())

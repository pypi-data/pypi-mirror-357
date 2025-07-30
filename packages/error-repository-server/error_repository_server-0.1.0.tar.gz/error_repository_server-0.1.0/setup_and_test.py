"""
Setup and test script for the Error Repository MCP Server
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package():
    """Install the package in development mode"""
    try:
        print("Installing error-repository-server package...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Package installed successfully")
            return True
        else:
            print(f"❌ Installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def test_server_import():
    """Test if the server can be imported"""
    try:
        print("Testing server import...")
        import error_repository_server.server
        print("✅ Server import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_database_load():
    """Test if the error database can be loaded"""
    try:
        print("Testing database load...")
        from error_repository_server.server import error_repo
        
        # Test basic functionality
        summary = error_repo.get_error_summary()
        if "error" not in summary:
            print(f"✅ Database loaded: {summary['total_errors']} errors found")
            
            # Test search functionality
            result = error_repo.search_by_error_code("E001")
            if "error" not in result:
                print(f"✅ Search test passed: Found {result['error_code']}")
            else:
                print(f"⚠️ Search test warning: {result['error']}")
            
            return True
        else:
            print(f"❌ Database error: {summary['error']}")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Run all setup and tests"""
    print("Error Repository MCP Server Setup and Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("❌ Please run this script from the project root directory")
        return False
    
    # Install package
    if not install_package():
        return False
    
    # Test import
    if not test_server_import():
        return False
    
    # Test database
    if not test_database_load():
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. You can now run the server with: python -m error_repository_server.server")
    print("2. The server is configured for VS Code MCP integration in .vscode/mcp.json")
    print("3. Use the server with GitHub Copilot for error resolution assistance")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# Test basic package functionality
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
def test_package_import():
    """Test that the package can be imported successfully."""
    import grep_mcp
    assert grep_mcp is not None

def test_package_version():
    """Test that the package version is correct."""
    import grep_mcp
    assert grep_mcp.__version__ == "1.0.3"

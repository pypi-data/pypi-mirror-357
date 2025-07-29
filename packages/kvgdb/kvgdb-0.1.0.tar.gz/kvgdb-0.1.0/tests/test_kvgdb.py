"""
Basic tests for kvgdb package.
"""
from kvgdb import __version__

def test_version():
    """Test that version is set correctly."""
    assert __version__ == "0.1.0" 
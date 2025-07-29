"""
Vibethon - Automatic Python Debugger with Interactive REPL
"""

from .vdb import CustomPdb

# Create a global instance that users can import
vdb = CustomPdb()

__version__ = "1.0.0"
__all__ = ["vdb"]
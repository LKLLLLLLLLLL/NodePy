import importlib
from pathlib import Path

from loguru import logger

from .base_node import _NODE_REGISTRY

"""
Auto-discovery and registration system for node modules.

This module automatically imports all Python files in the nodes/ directory tree,
triggering the @register_node decorators to populate the _NODE_REGISTRY.

Adding new nodes:
- Simply create a new .py file anywhere under nodes/
- Decorate your node class with @register_node
- No need to modify this __init__.py file!
"""


# Files to skip during auto-discovery (infrastructure, not node definitions)
_SKIP_FILES = {
    '__init__.py',
    'BaseNode.py',
}

def _auto_import_nodes():
    """
    Automatically discover and import all node modules.
    
    This function walks through all subdirectories under the nodes package,
    finds all .py files (except those in _SKIP_FILES), and imports them.
    This triggers the @register_node decorators, populating _NODE_REGISTRY.
    """
    # Get the nodes package directory
    nodes_dir = Path(__file__).parent
    
    # Recursively walk through all subdirectories
    for subdir in nodes_dir.iterdir():
        if not subdir.is_dir() or subdir.name.startswith('_'):
            continue
            
        # Get all .py files in this subdirectory and its children
        for py_file in subdir.rglob('*.py'):
            filename = py_file.name
            
            # Skip infrastructure files
            if filename in _SKIP_FILES:
                continue
            
            # Build the import path relative to the nodes package
            # e.g., "Generate.Const" or "Compute.String"
            relative_path = py_file.relative_to(nodes_dir)
            module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
            module_name = '.'.join(module_parts)
            
            # Import the module (triggers @register_node decorators)
            try:
                importlib.import_module(f'.{module_name}', package=__name__)
            except Exception as e:
                # Log the error but don't fail the entire import process
                logger.warning(f"Failed to import {module_name}: {e}")

# Run auto-discovery when this package is imported
_auto_import_nodes()

logger.info(f"Registered {len(list(_NODE_REGISTRY.keys()))} nodes: {list(_NODE_REGISTRY.keys())}")

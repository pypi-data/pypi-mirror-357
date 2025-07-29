"""
Load - Modern alternative to Python import
Inspired by Go and Groovy simplicity

Compatible with Python 2.7 and Python 3.5+
"""

# Handle Python 2/3 compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import types
import warnings
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

# Import only what we need from the compatibility layer
from ._compat import import_module  # Used in _import_common_aliases

# For Python 2/3 compatibility
PY2 = sys.version_info[0] == 2
PY3 = not PY2

# Type variable for generic function type
F = TypeVar('F', bound=Callable[..., Any])

# Import core functionality and configuration
from .core import (
    load_github,
    load_pypi,
    load_url,
    load_local,
    enable_auto_print,
    disable_auto_print,
    set_print_limit,
    info as core_info,
    load,
)
from .config import PRINT_LIMIT, AUTO_PRINT, PRINT_TYPES

__version__ = "1.0.0"
__author__ = "Tom Sapletta"
__email__ = "info@softreck.dev"

# Import utility functions first to avoid circular imports
from .utils import import_aliases, smart_print

# Define __all__ after all imports to avoid circular imports
__all__ = [
    'load',
    'load_github',
    'load_pypi',
    'load_url',
    'load_local',
    'enable_auto_print',
    'disable_auto_print',
    'set_print_limit',
    'info',
    'load_decorator',
    'test_cache_info',
    'import_aliases',
    'smart_print',
    'PRINT_LIMIT',
    'AUTO_PRINT',
    'PRINT_TYPES',
]


class LoadModule(object):
    """Magic module - everything through dot notation."""

    def __getattr__(self, name):
        """Get attribute from the module.

        Handles special module attributes and provides dynamic imports.
        """
        # First check for special module attributes
        special_attrs = {
            "__path__",
            "__file__",
            "__spec__",
            "__loader__",
            "__package__",
            "__annotations__",
            "__all__",
            "__builtins__",
        }

        if name in special_attrs:
            if name == "__all__":
                return [
                    "load_github",
                    "load_pypi",
                    "load_url",
                    "load_local",
                    "enable_auto_print",
                    "disable_auto_print",
                    "set_print_limit",
                    "info",
                    "load",
                ]
            return None

        # Then check for module-level methods
        if name in [
            "enable_auto_print",
            "disable_auto_print",
            "set_print_limit",
            "info",
        ]:
            # Check if the method exists in the instance's __dict__
            if name in self.__dict__:
                return self.__dict__[name]

        # Handle common Python module aliases
        common_aliases = {
            # Data science
            "np": "numpy",
            "pd": "pandas",
            "plt": "matplotlib.pyplot",
            "sns": "seaborn",
            # Machine learning
            "tf": "tensorflow",
            "torch": "torch",
            "sklearn": "sklearn",
            # Web and data
            "requests": "requests",
            "json": "json",
            "yaml": "yaml",
            # System
            "os": "os",
            "sys": "sys",
            "pathlib": "pathlib",
            # Image processing
            "cv2": "opencv-python",
            "PIL": "PIL",
            # Utilities
            "time": "time",
            "datetime": "datetime",
            "random": "random",
        }

        if name in common_aliases:
            module_name = common_aliases[name]
            try:
                module = __import__(module_name)
                # For submodules like matplotlib.pyplot
                if "." in module_name:
                    for part in module_name.split(".")[1:]:
                        module = getattr(module, part)
                # Cache the module in the instance
                setattr(self, name, module)
                return module
            except ImportError:
                raise ImportError(
                    "Could not import {0}. Please install it with: pip install {1}".format(name, module_name)
                )

        # Popular aliases mapping
        aliases = {
            # Data science
            "np": "numpy",
            "pd": "pandas",
            "plt": "matplotlib.pyplot",
            "sns": "seaborn",
            # Machine learning
            "tf": "tensorflow",
            "torch": "torch",
            "sklearn": "sklearn",
            # Web and data
            "requests": "requests",
            "yaml": "yaml",
            # System
            "os": "os",
            "sys": "sys",
            "pathlib": "pathlib",
            # Image processing
            "cv2": "opencv-python",
            "PIL": "PIL",
            # Utilities
            "time": "time",
            "datetime": "datetime",
            "random": "random",
        }

        if name in aliases:
            module_name = aliases[name]
            try:
                module = __import__(module_name)
                # For submodules like matplotlib.pyplot
                if "." in module_name:
                    for part in module_name.split(".")[1:]:
                        module = getattr(module, part)
                # Cache the module in the instance
                setattr(self, name, module)
                return module
            except ImportError:
                raise ImportError(
                    "Could not import {0}. Please install it with: pip install {1}".format(name, module_name)
                )

        # If not found, try to load as a module
        try:
            module = __import__(name)
            # For submodules like matplotlib.pyplot
            if "." in name:
                for part in name.split(".")[1:]:
                    module = getattr(module, part)
            # Cache the module in the instance
            setattr(self, name, module)
            return module
        except ImportError:
            raise ImportError("Could not import {0}".format(name))

    # Auto-print functions
    def enable_auto_print(self):
        """Enable automatic printing of results."""
        from .core import enable_auto_print as _enable_auto_print

        _enable_auto_print()

    def disable_auto_print(self):
        """Disable automatic printing of results."""
        from .core import disable_auto_print as _disable_auto_print

        _disable_auto_print()

    def set_print_limit(self, limit):
        """Set the maximum number of items to print.

        Args:
            limit: Maximum number of items to print
        """
        from .core import set_print_limit as _set_print_limit

        _set_print_limit(limit)

    def __dir__(self):
        """Return list of attributes for tab completion."""
        # Common Python aliases
        python_aliases = [
            # Data science
            "np",
            "pd",
            "plt",
            "sns",
            # Machine learning
            "tf",
            "torch",
            "sklearn",
            # Web and data
            "requests",
            "json",
            "yaml",
            # System
            "os",
            "sys",
            "pathlib",
            # Image processing
            "cv2",
            "PIL",
            # Utilities
            "time",
            "datetime",
            "random",
        ]

        # Module methods
        methods = [
            "load_github",
            "load_pypi",
            "load_url",
            "load_local",
            "enable_auto_print",
            "disable_auto_print",
            "set_print_limit",
            "info",
            "load",
        ]

        # Combine all attributes
        attrs = set(python_aliases + methods + list(self.__dict__.keys()))
        return sorted(attrs)


# Create a type-safe module replacement
class LoadModuleWrapper(LoadModule):
    """Wrapper to maintain module attributes and type safety.
    
    This wrapper ensures proper type hints and module attributes
    are maintained when replacing the module with our custom class.
    """

    __version__ = __version__
    __author__ = __author__
    __email__ = __email__
    __file__ = None
    __path__ = []
    __package__ = None
    __spec__ = None
    __loader__ = None
    __annotations__ = {}
    
    def __init__(self):
        """Initialize the module wrapper."""
        super(LoadModuleWrapper, self).__init__()


# Store the original module before replacing it
_original_module = sys.modules[__name__]

# Common Python aliases that will be available with 'from load import *'
COMMON_ALIASES = {
    # Core modules
    'os': 'os',
    'sys': 'sys',
    'json': 'json',
    # Web
    'requests': 'requests',
    'yaml': 'yaml',
    # Utilities
    'time': 'time',
    'datetime': 'datetime',
    'random': 'random',
    'pathlib': 'pathlib',
}


def _import_common_aliases():
    """Import and inject common aliases into the module's globals."""
    import importlib
    import sys

    # Get the module's globals
    module = sys.modules[__name__]
    globals_dict = module.__dict__

    for alias, module_name in COMMON_ALIASES.items():
        if alias not in globals_dict:  # Don't override existing attributes
            try:
                # Import the module
                module = importlib.import_module(module_name.split(".")[0])

                # Handle submodules (e.g., matplotlib.pyplot)
                if "." in module_name:
                    for part in module_name.split(".")[1:]:
                        module = getattr(module, part)

                # Add to globals
                globals_dict[alias] = module
            except ImportError:
                pass  # Silently skip if the module is not available


# Create and configure the module wrapper
module_wrapper = LoadModuleWrapper()
module_wrapper.__file__ = getattr(_original_module, '__file__', __file__)
module_wrapper.__path__ = getattr(_original_module, '__path__', [])  # type: ignore[assignment]
module_wrapper.__package__ = getattr(_original_module, '__package__', __package__ or "")
module_wrapper.__loader__ = getattr(_original_module, '__loader__', None)

# Python 3.4+ only attributes
if sys.version_info >= (3, 4):
    module_wrapper.__spec__ = getattr(_original_module, '__spec__', None)
    module_wrapper.__annotations__ = getattr(_original_module, '__annotations__', {})

# Create a new module and update it with our wrapper's attributes
new_module = types.ModuleType(__name__)
for key, value in module_wrapper.__dict__.items():
    setattr(new_module, key, value)

# Add module-level functions
# Add core module functions
new_module.enable_auto_print = module_wrapper.enable_auto_print
new_module.disable_auto_print = module_wrapper.disable_auto_print
new_module.set_print_limit = module_wrapper.set_print_limit
new_module.info = core_info  # Use the already imported core_info

# Add decorator and utility functions
new_module.import_aliases = import_aliases  # Imported at the top
new_module.smart_print = smart_print  # Re-export smart_print

# Re-export config constants
new_module.PRINT_LIMIT = PRINT_LIMIT
new_module.AUTO_PRINT = AUTO_PRINT
new_module.PRINT_TYPES = PRINT_TYPES

# These will be added after their definitions
# We'll use a simple approach to expose these functions


def load_decorator(*modules: str, silent: bool = False, load_func: Optional[Callable[..., Any]] = None) -> Callable[[F], F]:
    """Decorator to preload dependencies before function execution.
    
    Args:
        *modules: Module names to preload. Can include aliases using 'alias=module_name' syntax.
        silent: If True, suppresses import messages.
        load_func: Optional function to use for loading modules (for testing).
        
    Returns:
        A decorator that will load the specified modules before function execution.
    """
    # Use the provided load function or the default one
    _load = load_func if load_func is not None else load
    
    # Track which modules we've already loaded
    loaded_modules = set()
    
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal loaded_modules
            
            for module_spec in modules:
                if module_spec in loaded_modules:
                    continue
                    
                try:
                    if '=' in module_spec:
                        alias, module_name = module_spec.split('=', 1)
                        globals()[alias] = _load(module_name, silent=silent)
                        loaded_modules.add(module_spec)
                    else:
                        _load(module_spec, silent=silent)
                        loaded_modules.add(module_spec)
                except ImportError as e:
                    if not silent:
                        print(f"Warning: Failed to load module: {e}")
                    # Continue to the next module even if one fails
                    continue
            
            # Execute the function regardless of whether all modules loaded successfully
            return func(*args, **kwargs)
                
        return cast(F, wrapper)
    return decorator


def test_cache_info() -> None:
    """Test and display cache information.

    Shows how to retrieve and display information about the module cache,
    including the number of cached modules and cache statistics.
    """
    print("\n🧪 Testing cache info...")

    # Import several modules (won't auto-print due to silent=True)
    modules = ["json", "os", "sys", "time", "math"]
    for module_name in modules:
        try:
            __import__(module_name)
        except ImportError:
            print(f"Warning: Failed to load {module_name}")

    # Get cache info
    cache_info = core_info()

    print("📊 Cache Statistics:")
    print(f"   Total cached modules: {cache_info['cache_size']}")
    print(f"   Auto-print enabled: {cache_info['auto_print']}")
    print(f"   Print limit: {cache_info['print_limit']}")
    cached = ", ".join(cache_info["cached_modules"])
    print(f"   Cached modules: {cached}")

    print("✅ Cache info test completed")


# Import and inject common aliases
_import_common_aliases()

# Now that all functions are defined, add them to the module
new_module.load_decorator = load_decorator
new_module.test_cache_info = test_cache_info

# Set __all__ on the new module
new_module.__all__ = __all__.copy()

# Replace the module in sys.modules
sys.modules[__name__] = new_module

# Add the import_aliases and load functions to the module
new_module.import_aliases = import_aliases
new_module.load = load

# Common Python aliases that will be available with 'from load import *'
__all__ = [
    # Core functions
    "load_github",
    "load_pypi",
    "load_url",
    "load_local",
    "enable_auto_print",
    "disable_auto_print",
    "set_print_limit",
    "info",
    "load",
    "import_aliases",
    # Add the helper function to __all__
    # Common data science aliases
    "np",
    "pd",
    "plt",
    "sns",
    # Machine learning
    "tf",
    "torch",
    "sklearn",
    # Web and data
    "requests",
    "json",
    "yaml",
    # System
    "os",
    "sys",
    "pathlib",
    # Image processing
    "cv2",
    "PIL",
    # Utilities
    "time",
    "datetime",
    "random",
]

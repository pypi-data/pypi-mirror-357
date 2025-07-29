"""
Shortcut functions for common packages
"""

from .core import load

# Shortcut functions
def load_pandas(alias="pd", install=True, force=False, silent=False):
    """Shortcut for loading pandas"""
    return load("pandas", alias=alias, install=install, force=force, silent=silent)


def load_numpy(alias="np", install=True, force=False, silent=False):
    """Shortcut for loading numpy"""
    return load("numpy", alias=alias, install=install, force=force, silent=silent)


def load_requests(install=True, force=False, silent=False):
    """Shortcut for loading requests"""
    return load("requests", install=install, force=force, silent=silent)


def load_json(install=True, force=False, silent=False):
    """Shortcut for loading json"""
    return load("json", install=install, force=force, silent=silent)


def load_os(install=True, force=False, silent=False):
    """Shortcut for loading os"""
    return load("os", install=install, force=force, silent=silent)


def load_sys(install=True, force=False, silent=False):
    """Shortcut for loading sys"""
    return load("sys", install=install, force=force, silent=silent)


def load_torch(install=True, force=False, silent=False):
    """Shortcut for loading torch"""
    try:
        return load("torch", install=install, force=force, silent=silent)
    except ImportError:
        if not silent:
            print("Warning: PyTorch is not installed. Install it with: pip install torch")
        raise


def load_cv2(install=True, force=False, silent=False):
    """Shortcut for loading OpenCV"""
    try:
        return load("cv2", alias="cv2", install=install, force=force, silent=silent)
    except ImportError:
        if not silent:
            print("Warning: OpenCV is not installed. Install it with: pip install opencv-python")
        raise


def load_pil(install=True, force=False, silent=False):
    """Shortcut for loading PIL"""
    try:
        return load("PIL", alias="PIL", install=install, force=force, silent=silent)
    except ImportError:
        if not silent:
            print("Warning: Pillow is not installed. Install it with: pip install pillow")
        raise


def load_sklearn(install=True, force=False, silent=False):
    """Shortcut for loading scikit-learn"""
    try:
        return load("sklearn", alias="sklearn", install=install, force=force, silent=silent)
    except ImportError:
        if not silent:
            print("Warning: scikit-learn is not installed. Install it with: pip install scikit-learn")
        raise


def load_matplotlib(alias="plt", install=True, force=False, silent=False):
    """Shortcut for loading matplotlib"""
    try:
        return load("matplotlib.pyplot", alias=alias, install=install, force=force, silent=silent)
    except ImportError:
        if not silent:
            print("Warning: matplotlib is not installed. Install it with: pip install matplotlib")
        raise


# Aliases
def np(install=True, force=False, silent=False):
    """Alias for numpy"""
    return load_numpy(install=install, force=force, silent=silent)


def pd(install=True, force=False, silent=False):
    """Alias for pandas"""
    return load_pandas(install=install, force=force, silent=silent)


def plt(install=True, force=False, silent=False):
    """Alias for matplotlib"""
    return load_matplotlib(install=install, force=force, silent=silent)


def tf(install=True, force=False, silent=False):
    """Alias for tensorflow"""
    try:
        return load("tensorflow", alias="tf", install=install, force=force, silent=silent)
    except ImportError:
        if not silent:
            print("Warning: TensorFlow is not installed. Install it with: pip install tensorflow")
        raise


def cv2(install=True, force=False, silent=False):
    """Alias for OpenCV"""
    return load_cv2(install=install, force=force, silent=silent)


def PIL(install=True, force=False, silent=False):
    """Alias for PIL"""
    return load_pil(install=install, force=force, silent=silent)


def sklearn(install=True, force=False, silent=False):
    """Alias for scikit-learn"""
    return load_sklearn(install=install, force=force, silent=silent)


# Add module-level shortcuts
requests = load_requests
json = load_json
os = load_os
sys = load_sys
def sys():
    return load("sys")

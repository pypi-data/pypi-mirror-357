# -*- coding: utf-8 -*-
"""
Registry management for Load
"""

import os
import subprocess
import sys
import tempfile
import zipfile

# Import compatibility layer
from ._compat import import_module, urlretrieve, urlopen  # noqa: F401

# Type hints for static type checkers (Python 2/3 compatible)
if False:  # MYPY
    from typing import Dict, Any, Optional, Tuple, Union, List, Set  # noqa: F401

# Global registry configurations
REGISTRIES = {
    "pypi": {
        "install_cmd": [sys.executable, "-m", "pip", "install"],
        "description": "PyPI - Official Python Package Index",
    },

    "github": {
        "install_cmd": [
            sys.executable,
            "-m",
            "pip",
            "install",
            "git+https://github.com/",
        ],
        "description": "GitHub repositories",
    },
    "gitlab": {
        "install_cmd": [
            sys.executable,
            "-m",
            "pip",
            "install",
            "git+https://gitlab.com/",
        ],
        "description": "GitLab repositories",
    },
    "url": {"install_cmd": None, "description": "Direct URL download"},
    "local": {"install_cmd": None, "description": "Local files and directories"},
}

# Private registries
PRIVATE_REGISTRIES = {
    "company": {
        "index_url": "https://pypi.company.com/simple/",
        "install_cmd": [sys.executable, "-m", "pip", "install", "--index-url"],
        "description": "Company private PyPI",
    },
    "private_gitlab": {
        "base_url": "https://gitlab.company.com/",
        "token": os.getenv("GITLAB_TOKEN"),
        "install_cmd": None,
        "description": "Private GitLab with token",
    },
}


class LoadRegistry(object):
    """Registry manager for Load
    
    This class handles package installation from various sources including PyPI,
    GitHub, GitLab, and direct URLs. It maintains a temporary directory for
    downloaded packages and tracks imported modules.
    """

    def __init__(self):
        # type: () -> None
        """Initialize the registry with a temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self._imported_modules = set()  # type: Set[str]  # Track imported modules

    @staticmethod
    def parse_source(name):
        # type: (str) -> tuple
        """Parse package source.
        
        Args:
            name: The package name or source to parse.
            
        Returns:
            tuple: A tuple containing (registry, name).
        """
        if "://" in name:
            return ("url", name)
        elif "/" in name:
            parts = name.split("/")
            # Check if the first part is a known private registry
            if parts[0] in PRIVATE_REGISTRIES:
                return parts[0], name
            # Check for GitHub/GitLab URLs
            elif "github.com" in name:
                return "github", name
            elif "gitlab.com" in name:
                return "gitlab", name
            # Default to GitHub for user/repo format
            elif len(parts) == 2 and "." not in parts[0]:
                return "github", name
            else:
                # If not matched above, treat as PyPI package with slash in name
                return "pypi", name
        elif name.endswith(".py") or name.startswith("./") or name.startswith("../"):
            return "local", name
        else:
            return "pypi", name

    @staticmethod
    def install(self, name, registry=None, **kwargs):
        # type: (str, Optional[str], **Any) -> bool
        """Install a package from the specified registry.
        
        Args:
            name: The package name or source specifier
            registry: Optional registry name (auto-detected if None)
            **kwargs: Additional keyword arguments for the installer
            
        Returns:
            bool: True if installation was successful, False otherwise
            
        Example:
            >>> registry = LoadRegistry()
            >>> registry.install("requests")  # Install from PyPI
            >>> registry.install("user/repo", registry="github")  # Install from GitHub
        """
        if registry is None:
            registry, name = self.parse_source(name)

        installers = {
            "pypi": self.install_from_pypi,
            "github": self.install_from_github,
            "gitlab": self.install_from_gitlab,
            "url": self.install_from_url,
        }
        
        installer = installers.get(registry)
        if installer is None:
            print("❌ Unknown registry: {0}".format(registry))
            return False
            
        return installer(name, **kwargs)

    @staticmethod
    def install_from_pypi(name, registry="pypi"):
        # type: (str, str) -> bool
        """Install from PyPI or private registry"""
        if registry in PRIVATE_REGISTRIES:
            config = PRIVATE_REGISTRIES[registry]
            cmd = config["install_cmd"].copy()
            if "index_url" in config:
                cmd.extend([config["index_url"], name])
            else:
                cmd.append(name)
        else:
            cmd = REGISTRIES["pypi"]["install_cmd"] + [name]

        print("📦 Installing {0} from {1}...".format(name, registry))
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    @classmethod
    def install_from_github(cls, repo):
        # type: (str) -> bool
        """Install from GitHub"""
        if not repo.startswith("https://"):
            repo = "https://github.com/{0}".format(repo)

        cmd = [sys.executable, "-m", "pip", "install", "git+{0}".format(repo)]
        print("📦 Installing from GitHub: {0}".format(repo))
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print("❌ Error installing from GitHub: {0}".format(e))
            return False

    @classmethod
    def install_from_gitlab(cls, repo, token=None):
        # type: (str, OptStr) -> bool
        """Install from GitLab"""
        if not repo.startswith("https://"):
            repo = "https://gitlab.com/{0}".format(repo)

        try:
            if token:
                repo_with_token = repo.replace(
                    "https://", "https://oauth2:{0}@".format(token)
                )
                cmd = [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "git+{0}".format(repo_with_token),
                ]
            else:
                cmd = [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "git+{0}".format(repo),
                ]

            print("📦 Installing from GitLab: {0}".format(repo))
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print("❌ Error installing from GitLab: {0}".format(e))
            return False

    def install_from_url(self, url):
        # type: (str) -> bool
        """Install a package from a URL.
        
        Supports .whl, .tar.gz, and .zip files. For .zip files, it looks for
        a setup.py file to install from.
        
        Args:
            url: URL of the package to install
            
        Returns:
            bool: True if installation was successful, False otherwise
        """
        try:
            # Download the file
            print("📦 Downloading from URL: {0}".format(url))
            filename = os.path.basename(url)
            filepath = os.path.join(self.temp_dir, filename)
            
            # Use urlretrieve from _compat for Python 2/3 compatibility
            urlretrieve(url, filepath)

            # Install based on file type
            if filepath.endswith((".whl", ".tar.gz")):
                cmd = [sys.executable, "-m", "pip", "install", filepath]
            elif filepath.endswith(".zip"):
                # Extract and install from setup.py
                with zipfile.ZipFile(filepath, "r") as zip_ref:
                    zip_ref.extractall(self.temp_dir)
                
                # Find setup.py in the extracted files
                setup_dir = None
                for root, _, files in os.walk(self.temp_dir):
                    if "setup.py" in files:
                        setup_dir = root
                        break
                
                if not setup_dir:
                    raise ValueError("No setup.py found in the downloaded package")
                
                # Change to the directory with setup.py and install
                original_dir = os.getcwd()
                try:
                    os.chdir(setup_dir)
                    cmd = [sys.executable, "setup.py", "install"]
                finally:
                    os.chdir(original_dir)
            else:
                raise ValueError("Unsupported file format")

            # Run the installation command
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print("❌ Installation failed with error:")
                print(result.stderr)
                return False

            return True

        except Exception as e:  # noqa: B902
            print("❌ Error installing from URL {0}: {1}".format(url, str(e)))
            return False


def add_registry(name, config):
    # type: (str, dict) -> None
    """Add new registry"""
    PRIVATE_REGISTRIES[name] = config


def list_registries():
    # type: () -> None
    """List available registries"""
    print("🔧 Available registries:")
    print("\n📦 Public:")
    for name, config in REGISTRIES.items():
        print("  {0}: {1}".format(name, config['description']))

    print("\n🔒 Private:")
    for name, config in PRIVATE_REGISTRIES.items():
        print("  {0}: {1}".format(name, config['description']))


def configure_private_registry(name, index_url=None, token=None, base_url=None):
    # type: (str, Optional[str], Optional[str], Optional[str]) -> None
    """Quick private registry configuration"""
    config = {"description": "Private registry: {0}".format(name)}

    if index_url:
        config.update(
            {
                "index_url": index_url,
                "install_cmd": [sys.executable, "-m", "pip", "install", "--index-url"],
            }
        )

    if token:
        config["token"] = token

    if base_url:
        config["base_url"] = base_url

    PRIVATE_REGISTRIES[name] = config
    print("✅ Configured private registry: {0}".format(name))

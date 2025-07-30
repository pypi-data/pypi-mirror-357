"""Auto-upgrade functionality for claude-monitor."""

import subprocess
import sys
import time
from typing import Optional, Tuple
import json
import urllib.request
import urllib.error
from packaging import version


def get_pypi_version(package_name: str = "claude-monitor") -> Optional[str]:
    """Get the latest version from PyPI.
    
    Args:
        package_name: Name of the package to check
        
    Returns:
        Latest version string or None if failed
    """
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
            return data["info"]["version"]
    except (urllib.error.URLError, KeyError, json.JSONDecodeError):
        return None


def get_installed_version(package_name: str = "claude-monitor") -> Optional[str]:
    """Get the currently installed version.
    
    Args:
        package_name: Name of the package to check
        
    Returns:
        Installed version string or None if not found
    """
    try:
        from importlib.metadata import version as get_version
        return get_version(package_name)
    except Exception:
        # Fallback to pip show
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        except subprocess.CalledProcessError:
            pass
    return None


def check_for_updates() -> Tuple[bool, Optional[str], Optional[str]]:
    """Check if a newer version is available.
    
    Returns:
        Tuple of (update_available, current_version, latest_version)
    """
    current = get_installed_version()
    latest = get_pypi_version()
    
    if not current or not latest:
        return False, current, latest
    
    try:
        return version.parse(latest) > version.parse(current), current, latest
    except Exception:
        return False, current, latest


def detect_package_manager() -> Optional[str]:
    """Detect which package manager was used to install claude-monitor.
    
    Returns:
        Package manager name or None if not detected
    """
    # Check if running from a specific virtual environment
    executable_path = sys.executable
    
    # Check for uv tool
    if "uv/tools" in executable_path:
        return "uv"
    
    # Check for pipx
    if "pipx/venvs" in executable_path:
        return "pipx"
    
    # Check for conda/mamba
    if "conda" in executable_path or "mamba" in executable_path:
        return "conda"
    
    # Check for poetry
    if "pypoetry" in executable_path:
        return "poetry"
    
    # Default to pip
    return "pip"


def perform_upgrade(package_name: str = "claude-monitor") -> bool:
    """Upgrade the package to the latest version.
    
    Args:
        package_name: Name of the package to upgrade
        
    Returns:
        True if upgrade successful, False otherwise
    """
    manager = detect_package_manager()
    
    print(f"🔄 Upgrading {package_name} to the latest version...")
    
    upgrade_commands = {
        "uv": ["uv", "tool", "upgrade", package_name],
        "pipx": ["pipx", "upgrade", package_name],
        "conda": ["conda", "update", "-y", package_name],
        "poetry": ["poetry", "update", package_name],
        "pip": [sys.executable, "-m", "pip", "install", "--upgrade", package_name],
    }
    
    # Try detected package manager first
    if manager and manager in upgrade_commands:
        try:
            result = subprocess.run(
                upgrade_commands[manager],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print(f"✅ Upgrade completed successfully with {manager}!")
                return True
            else:
                print(f"⚠️  {manager} upgrade failed, trying alternatives...")
        except FileNotFoundError:
            print(f"⚠️  {manager} not found, trying alternatives...")
    
    # Try all package managers in order
    for pm_name, command in upgrade_commands.items():
        if pm_name == manager:  # Skip already tried
            continue
            
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print(f"✅ Upgrade completed successfully with {pm_name}!")
                return True
        except FileNotFoundError:
            continue
    
    # Last resort: pip with --break-system-packages
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", package_name, "--break-system-packages"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print("✅ Upgrade completed successfully!")
            return True
    except:
        pass
    
    print("❌ Upgrade failed with all package managers")
    return False


def auto_upgrade_check(force: bool = False) -> None:
    """Check and perform auto-upgrade if needed.
    
    Args:
        force: Force upgrade even if already up to date
    """
    # Skip in development mode (when installed with -e)
    if get_installed_version() is None:
        return
    
    print("🔍 Checking for updates...")
    update_available, current, latest = check_for_updates()
    
    if not update_available and not force:
        return
    
    if update_available:
        print(f"📦 New version available: {latest} (current: {current})")
        
        # Auto-upgrade without asking
        if perform_upgrade():
            print("🎉 Please restart claude-monitor to use the new version")
            time.sleep(2)
            sys.exit(0)
    else:
        print(f"✅ Already up to date (version {current})")
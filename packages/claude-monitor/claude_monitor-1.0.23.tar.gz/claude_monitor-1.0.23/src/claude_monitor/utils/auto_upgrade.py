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


def perform_upgrade(package_name: str = "claude-monitor") -> bool:
    """Upgrade the package to the latest version.
    
    Args:
        package_name: Name of the package to upgrade
        
    Returns:
        True if upgrade successful, False otherwise
    """
    try:
        print(f"🔄 Upgrading {package_name} to the latest version...")
        
        # Use pip to upgrade
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.returncode == 0:
            print("✅ Upgrade completed successfully!")
            return True
        else:
            print(f"❌ Upgrade failed: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Upgrade failed: {e}")
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
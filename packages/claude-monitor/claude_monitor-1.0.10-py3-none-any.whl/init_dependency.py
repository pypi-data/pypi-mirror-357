import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

NODE_VERSION = "18.17.1"
NODE_DIST_URL = "https://nodejs.org/dist"

# Expected SHA256 checksums for Node.js v18.17.1
NODE_CHECKSUMS = {
    "node-v18.17.1-linux-x64.tar.xz": "07e76408ddb0300a6f46fcc9abc61f841acde49b45020ec4e86bb9b25df4dced",
    "node-v18.17.1-linux-arm64.tar.xz": "3f933716a468524acb68c2514d819b532131eb50399ee946954d4a511303e1bb",
    "node-v18.17.1-darwin-x64.tar.xz": "bb15810944a6f77dcc79c8f8da01a605473e806c4ab6289d0a497f45a200543b",
    "node-v18.17.1-darwin-arm64.tar.xz": "e33c6391a33187c4eccf62661c9da3a67aa50752abae8fe75214e7e57b9292cc",
}


def verify_checksum(filename, expected_checksum):
    """Verify the SHA256 checksum of a downloaded file."""
    print(f"Verifying checksum for {filename}...")
    sha256_hash = hashlib.sha256()

    try:
        with open(filename, "rb") as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)

        computed_checksum = sha256_hash.hexdigest()

        if computed_checksum == expected_checksum:
            print("✓ Checksum verification passed")
            return True
        else:
            print("✗ Checksum verification failed!")
            print(f"Expected: {expected_checksum}")
            print(f"Computed: {computed_checksum}")
            return False
    except FileNotFoundError:
        print(f"✗ File not found: {filename}")
        return False
    except Exception as e:
        print(f"✗ Error verifying checksum: {e}")
        return False


def is_node_available():
    """Check if Node.js and npm are available in the system PATH."""
    return shutil.which("node") and shutil.which("npm")


def ensure_npx():
    """Ensure npx is available by updating npm if necessary."""
    if shutil.which("npx"):
        return  # npx is already available

    if not shutil.which("npm"):
        print("npm is not available")
        sys.exit(1)

    print("npx is not available, updating npm to latest version...")
    try:
        # Update npm to latest version which includes npx
        subprocess.run(["npm", "install", "-g", "npm@latest"], check=True)
        print("npm updated successfully")

        # Check if npx is now available
        if not shutil.which("npx"):
            print("npx still not available, installing manually...")
            subprocess.run(["npm", "install", "-g", "npx"], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Failed to update npm: {e}")
        sys.exit(1)


def install_node_linux_mac():
    """Install Node.js on Linux or macOS systems and return the installation path."""
    system = platform.system().lower()
    arch = platform.machine()

    # Map architecture names to Node.js distribution naming
    if arch in ("x86_64", "amd64"):
        arch = "x64"
    elif arch in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        print(f"Unsupported architecture: {arch}")
        sys.exit(1)

    filename = f"node-v{NODE_VERSION}-{system}-{arch}.tar.xz"
    url = f"{NODE_DIST_URL}/v{NODE_VERSION}/{filename}"

    # Check if we have a known checksum for this file
    expected_checksum = NODE_CHECKSUMS.get(filename)
    if not expected_checksum:
        print(f"✗ No known checksum for {filename}")
        print("This may indicate an unsupported platform or version.")
        sys.exit(1)

    print(f"Downloading Node.js from {url}")
    urllib.request.urlretrieve(url, filename)

    # Verify checksum before extraction
    if not verify_checksum(filename, expected_checksum):
        print("✗ Checksum verification failed. Aborting installation for security.")
        print("The downloaded file may be corrupted or tampered with.")
        os.remove(filename)
        sys.exit(1)

    print("Extracting Node.js...")
    with tarfile.open(filename) as tar:
        tar.extractall("nodejs")
    os.remove(filename)

    # Find the extracted directory and add its bin folder to PATH
    extracted = next(d for d in os.listdir("nodejs") if d.startswith("node-v"))
    node_bin = os.path.abspath(f"nodejs/{extracted}/bin")
    os.environ["PATH"] = node_bin + os.pathsep + os.environ["PATH"]

    print("Node.js installed successfully and added to PATH.")
    return node_bin


def install_node_windows():
    """Install Node.js on Windows using MSI installer with user consent and return the installation path."""
    print("\nNode.js is required but not found on your system.")
    print(
        "This script can automatically install Node.js, but it requires administrator privileges."
    )
    print(f"Node.js version {NODE_VERSION} will be downloaded and installed.")

    while True:
        choice = (
            input(
                "\nDo you want to proceed with the automatic installation? (y/n/help): "
            )
            .lower()
            .strip()
        )

        if choice in ["y", "yes"]:
            break
        elif choice in ["n", "no"]:
            print("\nInstallation cancelled. Alternative installation options:")
            print("1. Download and install Node.js manually from: https://nodejs.org/")
            print("2. Use a package manager like Chocolatey: choco install nodejs")
            print("3. Use Scoop: scoop install nodejs")
            print("4. Use Windows Package Manager: winget install OpenJS.NodeJS")
            print("\nAfter installing Node.js, please run this script again.")
            sys.exit(0)
        elif choice == "help":
            print("\nAutomatic installation details:")
            print("- Downloads Node.js MSI installer from official source")
            print("- Runs: msiexec /i node-installer.msi /quiet /norestart")
            print("- Requires administrator privileges (UAC prompt may appear)")
            print("- Installs to: C:\\Program Files\\nodejs")
            continue
        else:
            print(
                "Please enter 'y' for yes, 'n' for no, or 'help' for more information."
            )

    print("Downloading Node.js MSI installer for Windows...")
    filename = os.path.join(tempfile.gettempdir(), "node-installer.msi")
    url = f"{NODE_DIST_URL}/v{NODE_VERSION}/node-v{NODE_VERSION}-x64.msi"

    try:
        urllib.request.urlretrieve(url, filename)
        print(f"✓ Downloaded installer ({os.path.getsize(filename)} bytes)")
    except urllib.error.URLError as e:
        print(f"\n❌ Failed to download Node.js installer from {url}")
        print(f"Network error: {e}")
        print("\n🔧 Next steps:")
        print("1. Check your internet connection")
        print("2. Download Node.js manually from: https://nodejs.org/")
        print("3. Try again later if the server is temporarily unavailable")
        sys.exit(1)
    except OSError as e:
        print(f"\n❌ Failed to save installer file to {filename}")
        print(f"File system error: {e}")
        print("\n🔧 Next steps:")
        print("1. Check disk space and permissions")
        print("2. Try running as administrator")
        print("3. Download Node.js manually from: https://nodejs.org/")
        sys.exit(1)

    print(
        "Running installer (administrator privileges required - UAC prompt may appear)..."
    )
    try:
        subprocess.run(
            ["msiexec", "/i", filename, "/quiet", "/norestart"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print("\n❌ Node.js installation failed.")
        print("\nCommon causes and solutions:")
        print("• Insufficient administrator privileges - Run as administrator")
        print("• Windows Installer service issues - Restart Windows Installer service")
        print("• MSI file corruption - Try downloading again")
        print("• Conflicting existing installation - Uninstall old Node.js first")

        if e.stderr:
            print(f"\nInstaller error output: {e.stderr.strip()}")
        if e.stdout:
            print(f"Installer output: {e.stdout.strip()}")
        print(f"Return code: {e.returncode}")

        print("\n🔧 Next steps:")
        print("1. Download and install Node.js manually from: https://nodejs.org/")
        print("2. Or use Windows Package Manager: winget install OpenJS.NodeJS")
        print("3. Or use Chocolatey: choco install nodejs")
        print("4. Restart your terminal after installation")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Windows Installer (msiexec) not found.")
        print("This indicates a serious Windows system issue.")
        print("\nPlease install Node.js manually from: https://nodejs.org/")
        sys.exit(1)
    except PermissionError:
        print("\n❌ Permission denied when running installer.")
        print("Please run this script as administrator or install Node.js manually.")
        print("\nManual installation: https://nodejs.org/")
        sys.exit(1)

    print("Node.js installed successfully.")
    node_path = "C:\\Program Files\\nodejs"
    os.environ["PATH"] = node_path + os.pathsep + os.environ["PATH"]

    print("Node.js installed successfully and added to PATH.")
    return node_path


def ensure_ccusage_available():
    """Ensure ccusage is available via npx."""
    try:
        # Find npm and npx commands - try multiple locations
        npm_cmd = shutil.which("npm")
        npx_cmd = shutil.which("npx")

        # If not found in PATH, check common installation locations
        if not npm_cmd:
            common_paths = [
                os.path.join(os.environ.get("HOME", ""), ".local", "bin", "npm"),
                "/usr/local/bin/npm",
                "/usr/bin/npm",
                "C:\\Program Files\\nodejs\\npm.cmd"
                if platform.system() == "Windows"
                else None,
            ]
            # Also check in the directory where we might have just installed Node.js
            if os.path.exists("nodejs"):
                for subdir in os.listdir("nodejs"):
                    if subdir.startswith("node-v"):
                        npm_path = os.path.join("nodejs", subdir, "bin", "npm")
                        if os.path.exists(npm_path):
                            common_paths.insert(0, os.path.abspath(npm_path))

            for path in common_paths:
                if path and os.path.exists(path):
                    npm_cmd = path
                    break

        if not npx_cmd:
            common_paths = [
                os.path.join(os.environ.get("HOME", ""), ".local", "bin", "npx"),
                "/usr/local/bin/npx",
                "/usr/bin/npx",
                "C:\\Program Files\\nodejs\\npx.cmd"
                if platform.system() == "Windows"
                else None,
            ]
            # Also check in the directory where we might have just installed Node.js
            if os.path.exists("nodejs"):
                for subdir in os.listdir("nodejs"):
                    if subdir.startswith("node-v"):
                        npx_path = os.path.join("nodejs", subdir, "bin", "npx")
                        if os.path.exists(npx_path):
                            common_paths.insert(0, os.path.abspath(npx_path))

            for path in common_paths:
                if path and os.path.exists(path):
                    npx_cmd = path
                    break

        if not npm_cmd or not npx_cmd:
            print("\n❌ npm or npx command not found even after installation.")
            print("PATH environment variable may not be updated in current process.")
            print("\n🔧 Please try:")
            print("1. Restart your terminal and run the command again")
            print("2. Or manually install ccusage: npm install -g ccusage")
            sys.exit(1)

        # Check if ccusage is available
        result = subprocess.run(
            [npx_cmd, "--no-install", "ccusage", "--version"],
            capture_output=True,
            text=True,
            env=os.environ.copy(),  # Use current environment
        )
        if result.returncode == 0:
            print("✓ ccusage is available")
            return  # ccusage is available

        print("Installing ccusage...")
        # Try global installation first
        try:
            result = subprocess.run(
                [npm_cmd, "install", "-g", "ccusage"],
                check=True,
                capture_output=True,
                text=True,
                env=os.environ.copy(),  # Use current environment
            )
            print("✓ ccusage installed globally")
        except subprocess.CalledProcessError as e:
            print("⚠️  Global installation failed, trying local installation...")
            if e.stderr:
                print(f"Global install error: {e.stderr.strip()}")

            # If global fails, install locally
            try:
                result = subprocess.run(
                    [npm_cmd, "install", "ccusage"],
                    check=True,
                    capture_output=True,
                    text=True,
                    env=os.environ.copy(),  # Use current environment
                )
                print("✓ ccusage installed locally")
            except subprocess.CalledProcessError as local_e:
                print("\n❌ Both global and local ccusage installation failed.")
                print("\nGlobal installation error:")
                if e.stderr:
                    print(f"  {e.stderr.strip()}")
                print(f"  Return code: {e.returncode}")

                print("\nLocal installation error:")
                if local_e.stderr:
                    print(f"  {local_e.stderr.strip()}")
                print(f"  Return code: {local_e.returncode}")

                print("\n🔧 Troubleshooting steps:")
                print("1. Check npm permissions: npm config get prefix")
                print("2. Try with sudo (Linux/Mac): sudo npm install -g ccusage")
                print("3. Check npm registry: npm config get registry")
                print("4. Clear npm cache: npm cache clean --force")
                print("5. Manual install: npm install -g ccusage")
                sys.exit(1)
        except FileNotFoundError:
            print("\n❌ npm command not found.")
            print("Node.js and npm must be installed first.")
            print("This should not happen if Node.js installation succeeded.")
            sys.exit(1)
        except PermissionError:
            print("\n❌ Permission denied when running npm.")
            print("Try running with elevated privileges or check npm permissions.")
            print("\nOn Linux/Mac: sudo npm install -g ccusage")
            print("On Windows: Run as administrator")
            sys.exit(1)
    except FileNotFoundError:
        print("\n❌ npx command not found.")
        print("Node.js and npm must be installed and available in PATH.")
        print("Please restart your terminal or check your Node.js installation.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during ccusage installation: {e}")
        print("\n🔧 Manual installation steps:")
        print("1. npm install -g ccusage")
        print("2. Or use npx: npx ccusage --version")
        print("3. Check Node.js installation: node --version")
        sys.exit(1)


def ensure_node_installed():
    """Ensure Node.js, npm, npx, and ccusage are all available."""
    print("Checking dependencies...")

    node_bin_path = None
    if not is_node_available():
        # Install Node.js if not present
        system = platform.system()
        if system in ("Linux", "Darwin"):
            node_bin_path = install_node_linux_mac()
        elif system == "Windows":
            node_bin_path = install_node_windows()
        else:
            print(f"Unsupported OS: {system}")
            sys.exit(1)

        # After installation, verify Node.js is now available
        # If we just installed Node.js, we need to use the full path
        if node_bin_path:
            # Update PATH for subprocess calls
            os.environ["PATH"] = node_bin_path + os.pathsep + os.environ.get("PATH", "")

            # Also update npm and npx paths for immediate use
            node_exe = os.path.join(node_bin_path, "node")
            npm_exe = os.path.join(node_bin_path, "npm")
            npx_exe = os.path.join(node_bin_path, "npx")

            # For Windows, add .cmd extension
            if platform.system() == "Windows":
                npm_exe += ".cmd"
                npx_exe += ".cmd"

            # Check if executables exist
            if not (os.path.exists(node_exe) or os.path.exists(node_exe + ".exe")):
                print(
                    "Error: Node.js installation completed but Node.js executable not found."
                )
                print(f"Expected location: {node_exe}")
                print(
                    "You may need to restart your terminal or manually add Node.js to your PATH."
                )
                sys.exit(1)
        else:
            print(
                "Error: Node.js installation completed but installation path not returned."
            )
            sys.exit(1)
    else:
        print("✓ Node.js and npm are available")

    # Node.js and npm are present, ensure npx is available
    ensure_npx()

    # Ensure ccusage is available
    ensure_ccusage_available()
    print("✓ All dependencies are ready")

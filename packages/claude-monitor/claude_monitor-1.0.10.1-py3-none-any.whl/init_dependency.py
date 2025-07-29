#!/usr/bin/env python3
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
NODE_CHECKSUMS = {
    "node-v18.17.1-linux-x64.tar.xz": "07e76408ddb0300a6f46fcc9abc61f841acde49b45020ec4e86bb9b25df4dced",
    "node-v18.17.1-linux-arm64.tar.xz": "3f933716a468524acb68c2514d819b532131eb50399ee946954d4a511303e1bb",
    "node-v18.17.1-darwin-x64.tar.xz":  "bb15810944a6f77dcc79c8f8da01a605473e806c4ab6289d0a497f45a200543b",
    "node-v18.17.1-darwin-arm64.tar.xz":"e33c6391a33187c4eccf62661c9da3a67aa50752abae8fe75214e7e57b9292cc",
}

def verify_checksum(filename, expected):
    print(f"Verifying checksum for {filename}...")
    h = hashlib.sha256()
    try:
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
    except FileNotFoundError:
        print(f"✗ File not found: {filename}")
        return False
    got = h.hexdigest()
    if got.lower() == expected.lower():
        print("✓ Checksum verification passed")
        return True
    print("✗ Checksum verification failed!")
    print(f"  expected: {expected}")
    print(f"  computed: {got}")
    return False

def is_node_available():
    return shutil.which("node") and shutil.which("npm")

def install_node_linux_mac():
    system = platform.system().lower()
    arch = platform.machine()
    if arch in ("x86_64", "amd64"):
        arch = "x64"
    elif arch in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        print(f"Unsupported arch: {arch}")
        sys.exit(1)

    fname = f"node-v{NODE_VERSION}-{system}-{arch}.tar.xz"
    url = f"{NODE_DIST_URL}/v{NODE_VERSION}/{fname}"
    chk = NODE_CHECKSUMS.get(fname)
    if not chk:
        print(f"No checksum for {fname}")
        sys.exit(1)

    print(f"Downloading Node.js from {url}")
    urllib.request.urlretrieve(url, fname)

    if not verify_checksum(fname, chk):
        os.remove(fname)
        sys.exit(1)

    print("Extracting Node.js...")
    with tarfile.open(fname) as tar:
        tar.extractall("nodejs")
    os.remove(fname)

    sub = next(d for d in os.listdir("nodejs") if d.startswith("node-v"))
    node_bin = os.path.abspath(f"nodejs/{sub}/bin")
    # EXPORT into this process so subprocess calls see it:
    os.environ["PATH"] = node_bin + os.pathsep + os.environ.get("PATH", "")
    print("Node.js installed and PATH updated.")
    return node_bin

def ensure_node_installed():
    print("Checking dependencies...")
    node_bin = None
    if not is_node_available():
        system = platform.system()
        if system in ("Linux","Darwin"):
            node_bin = install_node_linux_mac()
        else:
            print("Only Linux/macOS currently supported by this script.")
            sys.exit(1)
    else:
        print("✓ Node.js already present.")
    return node_bin

def ensure_ccusage_available(node_bin=None):
    """
    Install ccusage by calling npm-cli.js directly under node,
    avoiding the #!/usr/bin/env node shebang issue.
    """
    node_cmd = shutil.which("node")
    if not node_cmd and node_bin:
        node_cmd = os.path.join(node_bin, "node")
    if not node_cmd or not os.path.exists(node_cmd):
        print("❌ Could not locate node executable.")
        sys.exit(1)

    # Figure out where npm-cli.js lives:
    # If `npm` is on PATH, use its directory; otherwise assume <node_bin>/.. etc.
    npm_cmd = shutil.which("npm") or os.path.join(node_bin, "npm")
    npm_dir = os.path.dirname(npm_cmd)
    npm_cli = os.path.abspath(os.path.join(npm_dir, "..", "lib", "node_modules", "npm", "bin", "npm-cli.js"))
    if not os.path.exists(npm_cli):
        print(f"❌ Could not find npm-cli.js at {npm_cli}")
        sys.exit(1)

    def run_npm(args, desc):
        print(desc + "...")
        try:
            subprocess.run(
                [node_cmd, npm_cli] + args,
                check=True,
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )
            print(f"✓ {desc} succeeded")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ {desc} failed:")
            print(e.stderr.strip() or e.stdout.strip())
            return False

    # First, try a global install
    if run_npm(["install", "-g", "ccusage"], "Global ccusage install"):
        return
    # Fallback to local install
    if run_npm(["install", "ccusage"], "Local ccusage install"):
        print("Note: you may want to add ./node_modules/.bin to your PATH")
        return

    # Both failed
    print("\n❌ Both global and local ccusage installs failed.")
    print("🔧 Troubleshoot:")
    print("  • Check npm permissions: npm config get prefix")
    print("  • Try sudo for global: sudo npm install -g ccusage")
    print("  • Or use npx directly: npx --no-install ccusage")
    sys.exit(1)

if __name__ == "__main__":
    node_bin = ensure_node_installed()
    ensure_ccusage_available(node_bin)
    print("🎉 All set!")

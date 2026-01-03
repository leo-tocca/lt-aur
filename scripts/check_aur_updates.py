#!/usr/bin/env python3
"""
Check AUR packages for updates based on packages-list.yaml
- Creates packages if missing
- Warns about updates without overwriting modified PKGBUILDs
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional
import urllib.request
import urllib.parse
import json
import yaml

AUR_RPC_URL = "https://aur.archlinux.org/rpc/v5/info"

def get_aur_version(pkgname: str) -> Optional[str]:
    """Query AUR RPC for package version."""
    params = urllib.parse.urlencode({'arg[]': pkgname})
    url = f"{AUR_RPC_URL}?{params}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data['resultcount'] > 0:
                return data['results'][0]['Version']
    except Exception as e:
        print(f"❌ Error fetching {pkgname}: {e}", file=sys.stderr)
    return None

def get_local_version(pkgbuild_path: Path) -> Optional[str]:
    """Extract pkgver and pkgrel from PKGBUILD."""
    try:
        result = subprocess.run(
            ['bash', '-c', f'source {pkgbuild_path} && echo "$pkgver-$pkgrel"'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"⚠️  Error parsing {pkgbuild_path}: {e}", file=sys.stderr)
    return None

def download_aur_pkgbuild(pkgname: str, dest_dir: Path) -> bool:
    """Clone entire AUR package to destination directory."""
    aur_url = f"https://aur.archlinux.org/{pkgname}.git"
    temp_dir = dest_dir.parent / f"{pkgname}_temp"
    
    try:
        # Clone AUR repo
        subprocess.run(
            ['git', 'clone', '--depth=1', aur_url, str(temp_dir)],
            check=True, capture_output=True
        )
        
        # Create destination if needed
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all files except .git
        for item in temp_dir.iterdir():
            if item.name not in ['.git', '.gitignore']:
                target = dest_dir / item.name
                if item.is_file():
                    target.write_bytes(item.read_bytes())
                    print(f"  ✓ Copied {item.name}")
        
        # Cleanup
        subprocess.run(['rm', '-rf', str(temp_dir)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download {pkgname}: {e.stderr.decode() if e.stderr else 'Unknown error'}", file=sys.stderr)
        return False

"""
def load_packages_list() -> list:
   #Load packages from packages-list.yaml.s
    yaml_path = Path('packages-list.yaml')
    if not yaml_path.exists():
        print("❌ packages-list.yaml not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
            if 'lt-aur-packages' in data and isinstance(data['lt-aur-packages'], list):
                return data
            else:
                print("❌ packages-list.yaml should contain a list", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"❌ Error parsing packages-list.yaml: {e}", file=sys.stderr)
        sys.exit(1)

"""
def load_packages_list() -> list:
    #Load packages from packages-list.yaml.
    yaml_path = Path('packages-list.yaml')
    if not yaml_path.exists():
        print("❌ packages-list.yaml not found", file=sys.stderr)
        sys.exit(1)

    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
            if 'lt-aur-packages' in data and isinstance(data['lt-aur-packages'], list):
                return data['lt-aur-packages']
            else:
                print("❌ packages-list.yaml should contain a list under 'lt-aur-packages'", file=sys.stderr)
                sys.exit(1)
    except Exception as e:
        print(f"❌ Error parsing packages-list.yaml: {e}", file=sys.stderr)
        sys.exit(1)
    

def main():
    packages_dir = Path('packages')
    packages_dir.mkdir(exist_ok=True)
    
    # Load package list
    package_names = load_packages_list()
    print(f"📦 Found {len(package_names)} packages in packages-list.yaml\n")
    
    new_packages = []
    updates_available = []
    
    for pkgname in package_names:
        pkg_dir = packages_dir / pkgname
        pkgbuild = pkg_dir / 'PKGBUILD'
        
        aur_ver = get_aur_version(pkgname)
        if not aur_ver:
            print(f"⚠️  {pkgname}: Not found on AUR or query failed")
            continue
        
        # Case 1: Package doesn't exist locally
        if not pkgbuild.exists():
            print(f"🆕 {pkgname}: Downloading from AUR (version {aur_ver})")
            if download_aur_pkgbuild(pkgname, pkg_dir):
                new_packages.append(pkgname)
                print(f"✓  {pkgname}: Created\n")
            else:
                print(f"❌ {pkgname}: Download failed\n")
            continue
        
        # Case 2: Package exists, check version
        local_ver = get_local_version(pkgbuild)
        if not local_ver:
            print(f"⚠️  {pkgname}: Cannot parse local PKGBUILD\n")
            continue
        
        if local_ver != aur_ver:
            print(f"🔄 {pkgname}: Update available {local_ver} → {aur_ver}")
            updates_available.append({
                'name': pkgname,
                'old': local_ver,
                'new': aur_ver
            })
        else:
            print(f"✓  {pkgname}: Up to date ({local_ver})")
    
    # Commit new packages
    if new_packages:
        print(f"\n📝 Committing {len(new_packages)} new packages...")
        try:
            subprocess.run(['git', 'add', 'packages/'], check=True)
            pkg_list = ', '.join(new_packages)
            subprocess.run(
                ['git', 'commit', '-m', f'Add new packages: {pkg_list}'],
                check=True
            )
            print("✓  Committed new packages")
        except subprocess.CalledProcessError as e:
            print(f"❌ Commit failed: {e}")
    
    # Create informational commits for updates (without modifying files)
    if updates_available:
        print(f"\n🔔 {len(updates_available)} updates available (manual merge required):")
        for pkg in updates_available:
            print(f"   • {pkg['name']}: {pkg['old']} → {pkg['new']}")
        
        # Create empty commit with update info
        try:
            msg = "[UPDATE AVAILABLE] Manual merge required:\n\n"
            for pkg in updates_available:
                msg += f"- {pkg['name']}: {pkg['old']} → {pkg['new']}\n"
            msg += f"\nRun: git clone --depth=1 https://aur.archlinux.org/PKGNAME.git to merge manually"
            
            subprocess.run(
                ['git', 'commit', '--allow-empty', '-m', msg],
                check=True
            )
            print("✓  Created update notification commit")
        except subprocess.CalledProcessError as e:
            print(f"❌ Notification commit failed: {e}")
    
    if not new_packages and not updates_available:
        print("\n✅ All packages are up to date")
    
    sys.exit(0)

if __name__ == '__main__':
    main()

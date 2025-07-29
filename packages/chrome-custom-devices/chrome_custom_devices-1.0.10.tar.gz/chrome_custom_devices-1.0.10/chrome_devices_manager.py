#!/usr/bin/env python3
"""
Chrome Custom Devices Manager

A comprehensive tool to add custom device presets to Chrome DevTools.
Converts device specifications into Chrome-compatible JSON format and 
provides multiple installation methods.

Author: Chrome Custom Devices Project
License: MIT
"""

import json
import os
import sys
import argparse
import platform
import subprocess
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from devices import DEVICES, get_device_capabilities, get_user_agent, is_mobile_device

import sys
if sys.platform == "win32":
    import os
    import codecs
    os.environ["PYTHONIOENCODING"] = "utf-8"
    # Force UTF-8 encoding for stdout on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        # For older Python versions
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

class ChromeDevicesManager:
    """Main class for managing Chrome custom devices."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.chrome_paths = self._get_chrome_paths()
        
    def _get_chrome_paths(self) -> Dict[str, List[str]]:
        """Get Chrome profile paths for different platforms."""
        paths = {
            "windows": [
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome Beta\User Data"),
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome Dev\User Data"),
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome SxS\User Data"),  # Canary
            ],
            "darwin": [  # macOS
                os.path.expanduser("~/Library/Application Support/Google/Chrome"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome Beta"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome Dev"),
                os.path.expanduser("~/Library/Application Support/Google/Chrome Canary"),
                os.path.expanduser("~/Library/Application Support/Arc/User Data"),  # Arc browser
            ],
            "linux": [
                os.path.expanduser("~/.config/google-chrome"),
                os.path.expanduser("~/.config/google-chrome-beta"),
                os.path.expanduser("~/.config/google-chrome-unstable"),
                os.path.expanduser("~/.config/chromium"),
            ]
        }
        return paths.get(self.platform, [])
    
    def _is_chrome_running(self) -> bool:
        """Check if Chrome is currently running."""
        try:
            if self.platform == "windows":
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
                    capture_output=True, text=True, check=True
                )
                return "chrome.exe" in result.stdout
            elif self.platform == "darwin":
                result = subprocess.run(
                    ["pgrep", "-f", "Google Chrome"],
                    capture_output=True, text=True
                )
                return result.returncode == 0
            else:  # Linux
                result = subprocess.run(
                    ["pgrep", "-f", "chrome|chromium"],
                    capture_output=True, text=True
                )
                return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _find_chrome_profiles(self) -> List[Tuple[str, str]]:
        """Find all Chrome profiles on the system."""
        profiles = []
        
        for base_path in self.chrome_paths:
            if not os.path.exists(base_path):
                continue
                
            # Check for Default profile
            default_prefs = os.path.join(base_path, "Default", "Preferences")
            if os.path.exists(default_prefs):
                profiles.append((f"{base_path} (Default)", default_prefs))
            
            # Check for numbered profiles
            for item in os.listdir(base_path):
                if item.startswith("Profile "):
                    profile_prefs = os.path.join(base_path, item, "Preferences")
                    if os.path.exists(profile_prefs):
                        profiles.append((f"{base_path} ({item})", profile_prefs))
        
        return profiles
    
    def _create_device_json(self, device: Dict) -> Dict:
        """Convert device specification to Chrome DevTools JSON format."""
        capabilities = get_device_capabilities(device)
        user_agent = get_user_agent(device)
        is_mobile = is_mobile_device(device)
        
        return {
            "title": device["name"],
            "type": "unknown",
            "user-agent": user_agent,
            "capabilities": capabilities,
            "screen": {
                "device-pixel-ratio": device["dpr"],
                "vertical": {
                    "width": device["width"],
                    "height": device["height"]
                },
                "horizontal": {
                    "width": device["height"],
                    "height": device["width"]
                }
            },
            "modes": [
                {
                    "title": "",
                    "orientation": "vertical",
                    "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}
                },
                {
                    "title": "",
                    "orientation": "horizontal", 
                    "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}
                }
            ],
            "show-by-default": True,
            "dual-screen": False,
            "show": "Default",
            "user-agent-metadata": {
                "brands": [{"brand": "", "version": ""}],
                "fullVersionList": [{"brand": "", "version": ""}],
                "fullVersion": "",
                "platform": "",
                "platformVersion": "",
                "architecture": "",
                "model": "",
                "mobile": is_mobile
            }
        }
    
    def generate_devices_json(self, output_format: str = "vibranium") -> str:
        """Generate devices JSON in specified format."""
        devices_json = [self._create_device_json(device) for device in DEVICES]
        
        if output_format == "vibranium":
            filename = "devices.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(devices_json, f, indent=2, ensure_ascii=False)
            
            print(f"[SUCCESS] Generated {filename} for Vibranium CLI")
            print(f"[INSTALL] Install with: npx @pittankopta/vibranium add {filename}")
            
        elif output_format == "preferences":
            # Format for direct Preferences file insertion
            devices_string = json.dumps(devices_json, separators=(',', ':'), ensure_ascii=False)
            filename = "devices_preferences.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(devices_string)
            
            print(f"[SUCCESS] Generated {filename} for direct Preferences modification")
            
        elif output_format == "manual":
            filename = "devices_manual.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(devices_json, f, indent=2, ensure_ascii=False)
            
            # Create manual installation instructions
            instructions = self._create_manual_instructions()
            with open("MANUAL_INSTALLATION.md", 'w', encoding='utf-8') as f:
                f.write(instructions)
            
            print(f"[SUCCESS] Generated {filename} and MANUAL_INSTALLATION.md")
            print("[INFO] Follow the instructions in MANUAL_INSTALLATION.md")
        
        return filename
    
    def _create_manual_instructions(self) -> str:
        """Create manual installation instructions."""
        return """# Manual Installation Instructions

## Step 1: Close Chrome
Make sure Chrome is completely closed before proceeding.

## Step 2: Locate Chrome Preferences File

### Windows
```
%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default\\Preferences
```

### macOS
```
~/Library/Application Support/Google/Chrome/Default/Preferences
```

### Linux
```
~/.config/google-chrome/Default/Preferences
```

## Step 3: Backup Current Preferences
Copy the Preferences file to create a backup:
```bash
cp Preferences Preferences.backup
```

## Step 4: Edit Preferences File

1. Open the Preferences file in a text editor
2. Search for `"custom-emulated-device-list"` or `"customEmulatedDeviceList"`
3. If the key doesn't exist, add it to the `"devtools"` section:
   ```json
   "devtools": {
     "preferences": {
       "custom-emulated-device-list": []
     }
   }
   ```
4. Replace the empty array `[]` with the contents of `devices_manual.json`

## Step 5: Restart Chrome
Open Chrome and check DevTools > Settings > Devices to see your new devices.

## Troubleshooting

- If devices don't appear, verify the JSON syntax is correct
- Make sure Chrome was completely closed during modification
- Check that you're editing the correct profile's Preferences file
- Restore from backup if something goes wrong
"""
    
    def backup_preferences(self, profile_path: str) -> str:
        """Create a backup of Chrome Preferences file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.json"
        
        shutil.copy2(profile_path, backup_filename)
        print(f"[SUCCESS] Backup created: {backup_filename}")
        return backup_filename
    
    def install_devices(self, profile_path: Optional[str] = None) -> bool:
        """Install devices directly to Chrome Preferences."""
        if self._is_chrome_running():
            print("[WARNING] Chrome is currently running!")
            print("   Please close Chrome completely before installation.")
            response = input("Continue anyway? (y/N): ").lower()
            if response != 'y':
                return False
        
        # Find profiles if not specified
        if not profile_path:
            profiles = self._find_chrome_profiles()
            if not profiles:
                print("[ERROR] No Chrome profiles found!")
                return False
            
            if len(profiles) == 1:
                profile_name, profile_path = profiles[0]
                print(f"[PROFILE] Using profile: {profile_name}")
            else:
                print("[PROFILE] Multiple Chrome profiles found:")
                for i, (name, path) in enumerate(profiles):
                    print(f"   {i + 1}. {name}")
                
                try:
                    choice = int(input("Select profile (1-{}): ".format(len(profiles)))) - 1
                    if 0 <= choice < len(profiles):
                        profile_name, profile_path = profiles[choice]
                        print(f"[PROFILE] Using profile: {profile_name}")
                    else:
                        print("[ERROR] Invalid selection!")
                        return False
                except (ValueError, KeyboardInterrupt):
                    print("[ERROR] Installation cancelled!")
                    return False
        
        # Create backup
        backup_file = self.backup_preferences(profile_path)
        
        try:
            # Load current preferences
            with open(profile_path, 'r', encoding='utf-8') as f:
                preferences = json.load(f)
            
            # Ensure devtools.preferences structure exists
            if "devtools" not in preferences:
                preferences["devtools"] = {}
            if "preferences" not in preferences["devtools"]:
                preferences["devtools"]["preferences"] = {}
            
            # Generate devices JSON
            devices_json = [self._create_device_json(device) for device in DEVICES]
            
            # Update preferences with correct key name (Chrome changed this!)
            preferences["devtools"]["preferences"]["custom-emulated-device-list"] = devices_json
            
            # Write back to file
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, separators=(',', ':'), ensure_ascii=False)
            
            print(f"[SUCCESS] Successfully installed {len(DEVICES)} custom devices!")
            print("[INFO] Please restart Chrome to see the new devices in DevTools.")
            return True
            
        except Exception as e:
            print(f"[ERROR] Installation failed: {e}")
            print(f"[INFO] Restoring from backup: {backup_file}")
            shutil.copy2(backup_file, profile_path)
            return False
    
    def install_devices_all_profiles(self) -> bool:
        """Install devices to ALL Chrome profiles automatically."""
        if self._is_chrome_running():
            print("[WARNING] Chrome is currently running!")
            print("   For best results, please close Chrome and run this script again.")
            response = input("Continue anyway? (y/N): ").lower()
            if response != 'y':
                print("Installation cancelled.")
                return False
        
        # Find all profiles
        profiles = self._find_chrome_profiles()
        if not profiles:
            print("[ERROR] No Chrome profiles found!")
            print("   Please make sure Chrome is installed and has been run at least once.")
            return False
        
        print(f"[SCAN] Found {len(profiles)} Chrome profile(s):")
        for profile_name, profile_path in profiles:
            chrome_variant = "Chrome"
            if "Chrome Beta" in profile_path:
                chrome_variant = "Chrome Beta"
            elif "Chrome Dev" in profile_path:
                chrome_variant = "Chrome Dev"
            elif "Chrome Canary" in profile_path:
                chrome_variant = "Chrome Canary"
            elif "Arc" in profile_path:
                chrome_variant = "Arc"
            elif "chromium" in profile_path:
                chrome_variant = "Chromium"
            
            profile_short_name = "Default" if "Default" in profile_path else profile_name.split("(")[-1].rstrip(")")
            print(f"   * {chrome_variant} {profile_short_name}")
        
        print(f"\n[INSTALL] Installing custom devices to all profiles...")
        
        # Generate devices JSON once
        devices_json = [self._create_device_json(device) for device in DEVICES]
        
        success_count = 0
        total_count = len(profiles)
        
        for profile_name, profile_path in profiles:
            try:
                # Create backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"{profile_path}.backup_{timestamp}"
                shutil.copy2(profile_path, backup_file)
                
                # Load current preferences
                with open(profile_path, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
                
                # Ensure devtools.preferences structure exists
                if "devtools" not in preferences:
                    preferences["devtools"] = {}
                if "preferences" not in preferences["devtools"]:
                    preferences["devtools"]["preferences"] = {}
                
                # Update preferences
                preferences["devtools"]["preferences"]["custom-emulated-device-list"] = devices_json
                
                # Write back to file
                with open(profile_path, 'w', encoding='utf-8') as f:
                    json.dump(preferences, f, separators=(',', ':'), ensure_ascii=False)
                
                # Determine profile display name
                chrome_variant = "Chrome"
                if "Chrome Beta" in profile_path:
                    chrome_variant = "Chrome Beta"
                elif "Chrome Dev" in profile_path:
                    chrome_variant = "Chrome Dev"
                elif "Chrome Canary" in profile_path:
                    chrome_variant = "Chrome Canary"
                elif "Arc" in profile_path:
                    chrome_variant = "Arc"
                elif "chromium" in profile_path:
                    chrome_variant = "Chromium"
                
                profile_short_name = "Default" if "Default" in profile_path else profile_name.split("(")[-1].rstrip(")")
                print(f"[OK] {chrome_variant} {profile_short_name}")
                success_count += 1
                
            except Exception as e:
                # Restore from backup on failure
                try:
                    shutil.copy2(backup_file, profile_path)
                except:
                    pass
                print(f"[FAIL] {profile_name} (restored from backup)")
        
        print()
        if success_count == total_count:
            print(f"[SUCCESS] Successfully installed custom devices to all {total_count} Chrome profiles!")
        elif success_count > 0:
            print(f"[PARTIAL] Installed to {success_count} out of {total_count} profiles")
        else:
            print("[ERROR] Failed to install to any profiles")
            return False
        
        print()
        print("[INFO] Restart Chrome to see your new devices in DevTools > Settings > Devices")
        print(f"\n[DEVICES] Installed {len(DEVICES)} custom devices:")
        for device in DEVICES:
            print(f"   * {device['name']}")
        
        return success_count > 0
    
    def restore_from_backup(self, backup_file: str, profile_path: Optional[str] = None) -> bool:
        """Restore Chrome Preferences from backup."""
        if not os.path.exists(backup_file):
            print(f"[ERROR] Backup file not found: {backup_file}")
            return False
        
        if not profile_path:
            profiles = self._find_chrome_profiles()
            if not profiles:
                print("[ERROR] No Chrome profiles found!")
                return False
            
            if len(profiles) == 1:
                profile_name, profile_path = profiles[0]
                print(f"[RESTORE] Restoring to profile: {profile_name}")
            else:
                print("[PROFILE] Multiple Chrome profiles found:")
                for i, (name, path) in enumerate(profiles):
                    print(f"   {i + 1}. {name}")
                
                try:
                    choice = int(input("Select profile to restore (1-{}): ".format(len(profiles)))) - 1
                    if 0 <= choice < len(profiles):
                        profile_name, profile_path = profiles[choice]
                        print(f"[RESTORE] Restoring to profile: {profile_name}")
                    else:
                        print("[ERROR] Invalid selection!")
                        return False
                except (ValueError, KeyboardInterrupt):
                    print("[ERROR] Restore cancelled!")
                    return False
        
        try:
            shutil.copy2(backup_file, profile_path)
            print(f"[SUCCESS] Successfully restored from {backup_file}")
            print("[INFO] Please restart Chrome for changes to take effect.")
            return True
        except Exception as e:
            print(f"[ERROR] Restore failed: {e}")
            return False
    
    def list_profiles(self):
        """List all found Chrome profiles."""
        profiles = self._find_chrome_profiles()
        if not profiles:
            print("[ERROR] No Chrome profiles found!")
            return
        
        print("[PROFILES] Found Chrome profiles:")
        for i, (name, path) in enumerate(profiles):
            print(f"   {i + 1}. {name}")
            print(f"      Path: {path}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Chrome Custom Devices Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --output vibranium          Generate JSON for Vibranium CLI
  %(prog)s --install                   Install devices directly to Chrome
  %(prog)s --backup                    Create backup of current settings
  %(prog)s --restore backup.json       Restore from backup file
  %(prog)s --list-profiles             Show all Chrome profiles
        """
    )
    
    parser.add_argument(
        "--output", 
        choices=["vibranium", "preferences", "manual"],
        help="Generate output in specified format"
    )
    parser.add_argument(
        "--install", 
        action="store_true",
        help="Install devices directly to Chrome Preferences"
    )
    parser.add_argument(
        "--install-all", 
        action="store_true",
        help="Install devices to ALL Chrome profiles automatically"
    )
    parser.add_argument(
        "--backup", 
        action="store_true",
        help="Create backup of Chrome Preferences"
    )
    parser.add_argument(
        "--restore", 
        metavar="BACKUP_FILE",
        help="Restore Chrome Preferences from backup file"
    )
    parser.add_argument(
        "--list-profiles", 
        action="store_true",
        help="List all found Chrome profiles"
    )
    parser.add_argument(
        "--profile", 
        metavar="PATH",
        help="Specify Chrome profile Preferences file path"
    )
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    manager = ChromeDevicesManager()
    
    if args.list_profiles:
        manager.list_profiles()
    elif args.output:
        manager.generate_devices_json(args.output)
    elif args.install:
        manager.install_devices(args.profile)
    elif args.install_all:
        manager.install_devices_all_profiles()
    elif args.backup:
        profiles = manager._find_chrome_profiles()
        if profiles:
            if args.profile:
                if os.path.exists(args.profile):
                    manager.backup_preferences(args.profile)
                else:
                    print(f"[ERROR] Profile not found: {args.profile}")
            else:
                profile_name, profile_path = profiles[0]
                print(f"[BACKUP] Backing up profile: {profile_name}")
                manager.backup_preferences(profile_path)
        else:
            print("[ERROR] No Chrome profiles found!")
    elif args.restore:
        manager.restore_from_backup(args.restore, args.profile)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

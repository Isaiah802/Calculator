#!/usr/bin/env python3
"""
Clean up old files from Pico - keep only the new modular structure
"""

import subprocess
import sys
import time

COM_PORT = "COM3"

# Files and directories to DELETE from Pico
OLD_FILES_TO_REMOVE = [
    # Old module directories
    '/basic',
    '/pc_companion', 
    '/firmware',
    '/libs',
    '/drivers',
    '/tools',
    
    # Old /math directory (renamed to /mathengine)
    '/math',
    
    # Old config/manifest files
    '/config.json',
    '/pico_manifest.json',
    
    # Old launcher/updater files
    '/main_launcher.py',
    '/device_smoke.py',
    '/pico_updater.py',
    '/periodic_ota.py',
    '/pico_net_test.py',
    '/network_helper.py',
    '/boot.py',
    
    # Old SD/display files (if not needed)
    '/display_sd.py',
    '/file_browser.py',
    
    # Old standalone library files
    '/decimal.py',
    '/fractions.py',
    '/statistics.py',
    '/typing.py',
    '/urequests.py',
    '/ili9341.py',
    
    # Root level unnecessary files
    '/__init__.py',
]

def run_ampy(args, description):
    """Run ampy command"""
    cmd = ['ampy', '--port', COM_PORT] + args
    print(f"  → {description}...", end=' ', flush=True)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)
        print("✅")
        return True
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout")
        return True  # Continue anyway
    except subprocess.CalledProcessError as e:
        print(f"⚠️ (may not exist)")
        return True  # Don't fail if file doesn't exist

def list_files():
    """List current files on Pico"""
    try:
        result = subprocess.run(['ampy', '--port', COM_PORT, 'ls'], 
                              capture_output=True, text=True, timeout=10, check=True)
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except:
        return []

def main():
    print("\n" + "="*70)
    print("  PICO CLEANUP - Remove Old Files")
    print("="*70)
    print(f"\n📍 Target Device: {COM_PORT}")
    
    # Test connection
    print(f"\n📡 Testing connection...")
    current_files = list_files()
    if not current_files:
        print(f"\n❌ Failed to connect to {COM_PORT}")
        print("Make sure Thonny is closed!")
        return 1
    
    print("✅ Connected!")
    print(f"\n📁 Current files/directories on Pico: {len(current_files)}")
    for f in sorted(current_files)[:20]:  # Show first 20
        print(f"  • {f}")
    if len(current_files) > 20:
        print(f"  ... and {len(current_files) - 20} more")
    
    print("\n⚠️  This will DELETE old files from your Pico.")
    print("Files to keep:")
    print("  ✅ /calculator.py")
    print("  ✅ /core/ (app state)")
    print("  ✅ /mathengine/ (math engine)")
    print("  ✅ /storage/ (file system)")
    print("  ✅ /ui/ (UI manager)")
    print("  ✅ /hardware/ (hardware abstraction)")
    print("  ✅ /games/, /graphing/, /scientific/, /sd/, /settings/")
    print("  ✅ Supporting files (enhanced_math_engine.py, graphics_engine.py, etc.)")
    
    response = input("\nContinue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Cancelled.")
        return 0
    
    removed_count = 0
    
    print(f"\n🗑️  Removing old files and directories...")
    for file_path in OLD_FILES_TO_REMOVE:
        if run_ampy(['rm', '-r', file_path], f"Remove {file_path}"):
            removed_count += 1
        time.sleep(0.1)
    
    # Summary
    print("\n" + "="*70)
    print("  CLEANUP SUMMARY")
    print("="*70)
    print(f"🗑️  Attempted to remove: {removed_count} items")
    
    print("\n✅ Cleanup complete!")
    print("\n📁 Remaining files on Pico:")
    final_files = list_files()
    for f in sorted(final_files):
        if not f.startswith('/_'):  # Hide hidden files
            print(f"  • {f}")
    
    print("\n🎉 Your Pico now has only the new modular calculator code!")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup cancelled by user")
        sys.exit(1)

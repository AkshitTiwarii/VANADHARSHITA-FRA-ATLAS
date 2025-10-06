# Find Tesseract Installation Script
# Run this to locate where Tesseract is installed on your system

import os
import shutil
from pathlib import Path

print("🔍 Searching for Tesseract OCR installation...\n")

# Method 1: Check PATH
tesseract_in_path = shutil.which('tesseract')
if tesseract_in_path:
    print(f"✅ Found in PATH: {tesseract_in_path}")
else:
    print("❌ Not found in PATH")

print("\n" + "="*60)
print("Searching common installation locations...")
print("="*60 + "\n")

# Method 2: Check common locations
common_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Tesseract-OCR\tesseract.exe",
    r"C:\Users\Public\Tesseract-OCR\tesseract.exe",
    r"D:\Tesseract-OCR\tesseract.exe",
    r"D:\Program Files\Tesseract-OCR\tesseract.exe",
    r"E:\Tesseract-OCR\tesseract.exe",
]

found_paths = []
for path in common_paths:
    if os.path.exists(path):
        print(f"✅ Found: {path}")
        found_paths.append(path)
    else:
        print(f"❌ Not found: {path}")

# Method 3: Search all drives
print("\n" + "="*60)
print("Searching all available drives (this may take a moment)...")
print("="*60 + "\n")

import string
for drive in string.ascii_uppercase:
    drive_path = f"{drive}:\\"
    if os.path.exists(drive_path):
        try:
            for root, dirs, files in os.walk(drive_path):
                if 'tesseract.exe' in files:
                    full_path = os.path.join(root, 'tesseract.exe')
                    if full_path not in found_paths:
                        print(f"✅ Found: {full_path}")
                        found_paths.append(full_path)
                # Limit search depth to avoid taking too long
                if root.count(os.sep) - drive_path.count(os.sep) > 3:
                    dirs.clear()
        except (PermissionError, OSError):
            continue

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

if found_paths:
    print(f"\n✅ Found {len(found_paths)} Tesseract installation(s):\n")
    for i, path in enumerate(found_paths, 1):
        print(f"   {i}. {path}")
    
    print("\n📝 TO CONFIGURE:")
    print(f"\n1. Edit 'tesseract_config.py' file")
    print(f"2. Set: TESSERACT_PATH = r\"{found_paths[0]}\"")
    print(f"3. Restart AI service")
    print(f"\nOr run this command in PowerShell:")
    print(f'   Set-Content -Path "ai-service\\tesseract_config.py" -Value "TESSERACT_PATH = r\\\"{found_paths[0]}\\\""')
else:
    print("\n❌ No Tesseract installation found!")
    print("\n📥 TO INSTALL:")
    print("   1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   2. Install to: C:\\Program Files\\Tesseract-OCR")
    print("   3. Check 'Add to PATH' during installation")
    print("   4. Restart this script to verify")

print("\n" + "="*60)

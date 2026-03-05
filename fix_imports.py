"""
Fix NumPy/Pandas compatibility issues
Run this before starting the app
"""

import subprocess
import sys
import os

print("🔧 Fixing NumPy/Pandas compatibility...")
print("=" * 50)

# Uninstall conflicting packages
packages = ['numpy', 'pandas']
for package in packages:
    print(f"📦 Uninstalling {package}...")
    subprocess.run([sys.executable, '-m', 'pip', 'uninstall', package, '-y'], 
                   capture_output=True)

print("\n📦 Installing compatible versions...")
# Install exact compatible versions
subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy==1.23.5'])
subprocess.run([sys.executable, '-m', 'pip', 'install', 'pandas==1.5.3'])

print("\n✅ Fixed! Now run: streamlit run app.py")
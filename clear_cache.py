"""
Clear all caches and temp files
Run this before starting the app
"""

import shutil
from pathlib import Path

print("🧹 Cleaning caches...")

# Clear Streamlit media cache
media_cache = Path.home() / ".streamlit/media"
if media_cache.exists():
    shutil.rmtree(media_cache, ignore_errors=True)
    print("✅ Cleared media cache")

# Clear Streamlit cache
cache_dir = Path.home() / ".streamlit/cache"
if cache_dir.exists():
    shutil.rmtree(cache_dir, ignore_errors=True)
    print("✅ Cleared Streamlit cache")

# Clear Python cache
pycache = Path("__pycache__")
if pycache.exists():
    shutil.rmtree(pycache, ignore_errors=True)
    print("✅ Cleared Python cache")

print("\n✨ Ready to run!")
print("👉 Run: streamlit run app.py")
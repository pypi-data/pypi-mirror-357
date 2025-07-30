import time
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Determine base path (compatible with both .py and .exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent

# Resolve OUTPUT_DIR relative to app folder
default_output_dir = (BASE_DIR / os.getenv("OUTPUT_DIR", "AllJsons")).resolve()
CLEANUP_HOURS = int(os.getenv("CLEANUP_HOURS", "24"))

def delete_files_older_than(folder_path: Path, hours: int = CLEANUP_HOURS):
    now = time.time()
    cutoff = now - (hours * 3600)
    deleted_files = []

    if not folder_path.exists():
        print(f"🧹 Cleanup: Folder '{folder_path}' does not exist. Nothing to clean.")
        return

    for file in folder_path.glob("*.json"):
        if file.is_file() and file.stat().st_mtime < cutoff:
            file.unlink()
            deleted_files.append(file.name)

    if deleted_files:
        print(f"🧹 Cleanup: Deleted files older than {hours} hours:")
        for f in deleted_files:
            print(f"  - {f}")
    else:
        print(f"🧹 Cleanup: No files older than {hours} hours found.")

def cleanup_jsons(folder_path: Path = None):
    """Cleanup .json files older than CLEANUP_HOURS in folder_path (or default)."""
    if folder_path is None:
        folder_path = default_output_dir
    delete_files_older_than(folder_path, hours=CLEANUP_HOURS)

if __name__ == "__main__":
    cleanup_jsons()
# 
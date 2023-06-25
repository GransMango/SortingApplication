import os
import shutil
from pathlib import Path
import json

# Default category directories
default_path = str(Path.home()) + "\\Downloads"

# Load categories from file
try:
    with open('categories.json', 'r') as file:
        categories = json.load(file)
except FileNotFoundError:
    # If the file doesn't exist, use the default categories
    categories = {
        "Music": [".mp3", ".flac", ".wav", ".ogg", ".m4a", ".aac"],
        "Documents": [".doc", ".docx", ".pdf", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".rtf", ".tex",
                      ".ods"],
        "Videos": [".mp4", ".mkv", ".flv", ".avi", ".mov", ".wmv", ".mpeg", ".mpg"],
        "Programs": [".exe", ".msi", ".dmg", ".pkg", ".app", ".deb", ".rpm", ".jar", ".bat", ".sh"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".tiff", ".ico", ".raw"],
        "Compressed": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".cs", ".php", ".go", ".rb", ".swift"],
        "eBooks": [".epub", ".mobi", ".azw", ".azw3", ".pdf"],
        "Torrents": [".torrent"],
        "Other": []  # For files that don't fit into any category
    }

try:
    with open('category_directories.json', 'r') as file:
        category_directories = json.load(file)
except FileNotFoundError:
    # If the file doesn't exist, use the default category directories
    category_directories = {category: os.path.join(default_path, category) for category in categories.keys()}

def sort_files():
    """Sort the files in the Downloads directory."""
    path = str(Path.home()) + "\\Downloads"
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file():  # Ignore directories
                ext = Path(entry).suffix.lower()
                for category, extensions in categories.items():
                    if ext in extensions:
                        old_path = os.path.join(path, entry.name)
                        new_path = os.path.join(category_directories[category], entry.name)
                        shutil.move(old_path, new_path)
                        break  # If file moved, no need to check remaining categories
                else:  # If no category matched, move to "Other"
                    old_path = os.path.join(path, entry.name)
                    new_path = os.path.join(category_directories["Other"], entry.name)
                    shutil.move(old_path, new_path)

if __name__ == "__main__":
    sort_files()

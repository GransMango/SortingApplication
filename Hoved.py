import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from ttkthemes import ThemedTk
import threading
import queue
import json


# Load categories from file
default_path = str(Path.home()) + "\\Downloads"
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

# remaining part of the code

def select_directory(category, label):
    """Open a directory selection dialog and set the chosen directory for the category."""
    directory = filedialog.askdirectory()
    if directory:  # If a directory was chosen
        # Move files from the old directory to the new one
        old_directory = category_directories[category]
        for filename in os.listdir(old_directory):
            shutil.move(os.path.join(old_directory, filename), directory)

        # Update the category directory
        category_directories[category] = directory
        label.config(text=directory)

        # Save the updated category_directories to a JSON file
        with open('category_directories.json', 'w') as file:
            json.dump(category_directories, file)


def sort_files(progress_queue, sorted_files_label, sort_button):
    """Sort the files in the Downloads directory."""
    path = str(Path.home()) + "\\Downloads"

    # Get the total number of files
    total_files = len([entry for entry in os.scandir(path) if entry.is_file()])
    sorted_files = 0

    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file():  # Ignore directories
                ext = Path(entry).suffix.lower()
                for category, extensions in categories.items():
                    if ext in extensions:
                        old_path = os.path.join(path, entry.name)
                        new_path = os.path.join(category_directories[category], entry.name)
                        shutil.move(old_path, new_path)
                        sorted_files += 1
                        progress_queue.put((sorted_files / total_files, sorted_files))  # Put the progress fraction and number of sorted files in the queue
                        break  # If file moved, no need to check remaining categories
                else:  # If no category matched, move to "Other"
                    old_path = os.path.join(path, entry.name)
                    new_path = os.path.join(category_directories["Other"], entry.name)
                    shutil.move(old_path, new_path)
                    sorted_files += 1
                    progress_queue.put((sorted_files / total_files, sorted_files))  # Put the progress fraction and number of sorted files in the queue

    # Change the button's color to light green after sorting and then change it back to original color after a few seconds
    sort_button.config(style='Sort.TButton')
    root.after(2000, lambda: sort_button.config(style='TButton'))  # Change it back to original color after 2 seconds

# Create the main window
root = ThemedTk(theme="arc")  # Using the "arc" theme
style = ttk.Style(root)
style.configure('Sort.TButton', background='light green')

# Create a frame and a button for each category
for category in categories.keys():
    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=5)

    label = ttk.Label(frame, text=category_directories[category], width=80)
    label.pack(side=tk.LEFT, padx=10)

    button = ttk.Button(frame, text=f"Select directory for {category}", command=lambda category=category, label=label: select_directory(category, label))
    button.pack(side=tk.LEFT)



# Create a progress bar
progress = ttk.Progressbar(root, length=400)
progress.pack(padx=10, pady=10)

# Create a label to display the number of sorted files
sorted_files_label = ttk.Label(root, text="0 files sorted")
sorted_files_label.pack(padx=10, pady=10)

# Create a button to start sorting files
sort_button = ttk.Button(root, text="Sort files", command=lambda: threading.Thread(target=sort_files, args=(queue.Queue(), sorted_files_label, sort_button)).start())
sort_button.pack(padx=10, pady=10)

# Update the progress bar and the sorted files label
def update_progress(progress_queue, sorted_files_label):
    try:
        # Update the progress bar and the sorted files label
        fraction, sorted_files = progress_queue.get_nowait()
        progress['value'] = fraction * 100  # ttk.Progressbar requires the value to be between 0 and 100
        sorted_files_label.config(text=f"{sorted_files} files sorted")

        # Schedule the next update
        root.after(100, update_progress, progress_queue, sorted_files_label)
    except queue.Empty:
        pass  # If the queue is empty, do nothing

def open_settings():
    """Open the settings window."""
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    # Create a frame and entry widgets for each category
    for category, extensions in categories.items():
        frame = ttk.Frame(settings_window)
        frame.pack(padx=10, pady=5)

        ttk.Label(frame, text=category).pack(side=tk.LEFT, padx=10)

        entry = ttk.Entry(frame)
        entry.insert(0, ', '.join(extensions))
        entry.pack(side=tk.LEFT, padx=10)

    ttk.Button(settings_window, text="Save", command=lambda: save_settings(settings_window)).pack(padx=10, pady=10)

def save_settings(settings_window):
    """Save the settings."""
    for widget in settings_window.winfo_children():
        if isinstance(widget, ttk.Frame):
            category = widget.winfo_children()[0].cget("text")
            extensions = widget.winfo_children()[1].get().split(', ')
            categories[category] = extensions

    # Save categories to file
    with open('categories.json', 'w') as file:
        json.dump(categories, file)

    # Close the settings window
    settings_window.destroy()

# Create a button to open the settings
settings_button = ttk.Button(root, text="Settings", command=open_settings)
settings_button.pack(padx=10, pady=10)

# Start the main loop
root.mainloop()

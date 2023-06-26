import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
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
    category_directories = {category: os.path.join(default_path, category) for category in categories.keys()}

def update_extensions(event):
    """Update the extensions associated with a category."""
    text_widget = event.widget
    category = text_widget.category
    new_extensions = text_widget.get(1.0, 'end-1c').split(", ")
    categories[category] = new_extensions

    with open('categories.json', 'w') as file:
        json.dump(categories, file)

def change_downloads_directory(label):
    """Open a directory selection dialog and set the chosen directory as the new downloads directory."""
    global default_path  # Use the global default_path variable
    directory = filedialog.askdirectory()
    if directory:  # If a directory was chosen
        # Update the downloads directory
        default_path = directory
        label.config(text=f"Current downloads directory: {default_path}")

        # Update the category directories to the new downloads directory
        category_directories = {category: os.path.join(default_path, category) for category in categories.keys()}

        # Save the updated category_directories to a JSON file
        with open('category_directories.json', 'w') as file:
            # Add the default_path to the category directories
            json.dump({**category_directories, "default_path": default_path}, file)

def select_directory(category, label):
    directory = filedialog.askdirectory()
    if directory:
        old_directory = category_directories[category]
        for filename in os.listdir(old_directory):
            shutil.move(os.path.join(old_directory, filename), directory)

        category_directories[category] = directory
        label.config(text=directory)

        with open('category_directories.json', 'w') as file:
            json.dump(category_directories, file)


def sort_files(progress_queue, sorted_files_label, sort_button):
    """Sort the files in the Downloads directory."""
    path = default_path  # Use the global default_path variable

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

def create_settings_frame(notebook):
    settings_frame = ttk.Frame(notebook)
    settings_notebook = ttk.Notebook(settings_frame)

    downloads_dir_frame = ttk.Frame(settings_notebook)

    downloads_dir_label = ttk.Label(downloads_dir_frame, text=f"Current downloads directory: {default_path}")
    downloads_dir_label.pack(pady=10)

    change_downloads_dir_button = ttk.Button(downloads_dir_frame, text="Change Downloads Directory",
                                             command=lambda: change_downloads_directory(downloads_dir_label))
    change_downloads_dir_button.pack()

    settings_notebook.add(downloads_dir_frame, text='Downloads Directory')

    rules_frame = ttk.Frame(settings_notebook)

    for category, extensions in categories.items():
        frame = ttk.Frame(rules_frame)
        frame.pack(padx=10, pady=5, fill=tk.X)  # Fill horizontally for left alignment

        text = tk.Text(frame, width=60, height=1, bd=0, bg="#add8e6", fg="black")  # Modified appearance
        text.insert(1.0, ', '.join(extensions))
        text.category = category
        text.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X)  # Aligned to left with some padding
        text.bind('<FocusOut>', update_extensions)

        label = ttk.Label(frame, text=category)  # Added a label
        label.pack(side=tk.RIGHT, padx=10)

    settings_notebook.add(rules_frame, text='Rules')

    settings_notebook.pack(expand=1, fill='both')

    return settings_frame




# imports and definitions stay the same until here...

# Create the main window
root = ThemedTk(theme="arc")  # Using the "arc" theme
style = ttk.Style(root)
style.configure('Sort.TButton', background='light green')

notebook = ttk.Notebook(root)  # This is the container for tabs

# Tab for Categories
categories_frame = ttk.Frame(notebook)

for category in categories.keys():
    frame = ttk.Frame(categories_frame)
    frame.pack(padx=10, pady=5)

    label = ttk.Label(frame, text=category_directories[category], width=80)
    label.pack(side=tk.LEFT, padx=10)

    button = ttk.Button(frame, text=f"Select directory for {category}",
                        command=lambda category=category, label=label: select_directory(category, label))
    button.pack(side=tk.LEFT)

notebook.add(categories_frame, text='Categories')

# Tab for Settings
settings_frame = create_settings_frame(notebook)
notebook.add(settings_frame, text='Settings')

notebook.pack(expand=1, fill='both')

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

# Start the main loop
root.mainloop()

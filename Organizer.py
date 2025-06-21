import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import atexit

CATEGORIES = {
    "images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "docs": [".pdf", ".docx", ".txt", ".md", ".xcl"],
    "audio": [".mp3", ".wav", ".flac", ".wav"],
    "videos": [".mp4", ".mov", ".avi"],
    "archives": [".zip", ".tar", ".gz", ".rar"],
    "code": [".py", ".js", ".html", ".css"],
    "executables": [".exe"]
}

current_log_file = None

def log_move(source, destination):
    global current_log_file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if current_log_file is None:
        current_log_file = os.path.join(os.path.dirname(source), ".organizer_log.txt")
    with open(current_log_file, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | Moved: {source} → {destination}\n")


def undo_last_organization(target_path):
    global current_log_file
    if current_log_file is None:
        current_log_file = os.path.join(target_path, ".organizer_log.txt")

    if not os.path.exists(current_log_file):
        messagebox.showwarning("No Log", "No undo history found!")
        return

    try:
        with open(current_log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        messagebox.showerror("Error", "Log file corrupted (encoding issue).")
        return

    if not lines:
        messagebox.showwarning("Empty Log", "Nothing to undo!")
        return

    last_move = lines[-1].strip().split(" | Moved: ")[1]
    source, destination = last_move.split(" → ")

    try:
        shutil.move(destination, source)
        with open(current_log_file, "w", encoding="utf-8") as f:
            f.writelines(lines[:-1])
        messagebox.showinfo("Undo Success", f"Reverted: {os.path.basename(source)}")
    except Exception as e:
        messagebox.showerror("Undo Failed", str(e))

def cleanup_log():
    global current_log_file
    if current_log_file and os.path.exists(current_log_file):
        try:
            os.remove(current_log_file)
        except Exception as e:
            print(f"Couldn't delete log: {e}")  # Silent fail, don't annoy user

atexit.register(cleanup_log)

def organize_folder(target_path):
    global current_log_file
    try:
        #Creates folders for organizing (will make an images folder even if no image )
        for category in CATEGORIES:
            os.makedirs(os.path.join(target_path, category), exist_ok=True)

        #Resets log file path to current
        current_log_file = os.path.join(target_path, ".organizer_log.txt")

        #skip subfolders (hopefully)
        for filename in os.listdir(target_path):
            file_path = os.path.join(target_path, filename)
            if os.path.isdir(file_path):
                continue

            _, ext = os.path.splitext(filename)
            ext = ext.lower()

            for category, extensions in CATEGORIES.items():
                if ext in extensions:
                    dest_folder = os.path.join(target_path, category)
                    dest_path = os.path.join(dest_folder, filename)
                    shutil.move(file_path, dest_path)
                    log_move(file_path, dest_path)
                    break

        messagebox.showinfo("Success", f"Organized files in:\n{target_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to organize:\n{e}")


def select_folder():
    folder_path = filedialog.askdirectory(title="Select Folder to Organize")
    if folder_path:
        organize_folder(folder_path)

#Gui and stuff
root = tk.Tk()
root.title("File Organizer (Auto-Clean)")

tk.Label(root, text="Select a folder to organize:").pack(pady=10)
tk.Button(root, text="Choose Folder", command=select_folder).pack(pady=5)
tk.Button(root, text="UNDO Last Move",
          command=lambda: undo_last_organization(filedialog.askdirectory())).pack(pady=5)
tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

root.protocol("WM_DELETE_WINDOW", root.quit)

root.mainloop()
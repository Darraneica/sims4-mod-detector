import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import platform
from scan_files import scan_mods_folder

root = tk.Tk()
root.title("The Sims 4 Mod Detector")
root.geometry("900x600")
root.resizable(True, True)

heading = tk.Label(root, text="The Sims 4 Mod Detector", font=("Charter", 18, "bold"), bg="#FF69B4", fg="white")
heading.pack(fill=tk.X)

table_frame = tk.Frame(root)
table_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

columns = ("name", "size", "last_modified", "path", "type")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tree.heading("name", text="Filename")
tree.heading("size", text="Size (MB)")
tree.heading("last_modified", text="Last Modified")
tree.heading("path", text="File Path")
tree.heading("type", text="Type")

tree.column("name", width=180)
tree.column("size", width=80, anchor="center")
tree.column("last_modified", width=150, anchor="center")
tree.column("path", width=350)
tree.column("type", width=100, anchor="center")

tree.tag_configure("good", background="#09cf27")      
tree.tag_configure("duplicate", background="#e9dc28") 
tree.tag_configure("bad", background="#c30000")       

button_frame = tk.Frame(root)
button_frame.pack(pady=5, fill=tk.X)

folder_label = tk.Label(button_frame, text="No folder selected", anchor="w")
folder_label.pack(side=tk.LEFT, padx=5)

def open_folder_dialog():
    folder_selected = filedialog.askdirectory(title="Select Sims 4 Mods Folder")
    if folder_selected:
        folder_label.config(text=folder_selected)
        scan_and_display(folder_selected)

select_folder_button = tk.Button(button_frame, text="Select Mods Folder", command=open_folder_dialog)
select_folder_button.pack(side=tk.LEFT, padx=5)

def is_bad_mod(mod):
    return mod["size_mb"] > 100

current_folder = None

def scan_and_display(folder_path):
    global current_folder
    current_folder = folder_path
    for row in tree.get_children():
        tree.delete(row)

    mods, duplicates = scan_mods_folder(folder_path)
    if not mods:
        tree.insert("", "end", values=("No mods found", "", "", "", ""))
        status_text.set("No mods found")
        return

    duplicate_names = set(duplicates.keys())


    mod_entries = []
    for mod in mods:
        if mod["name"] in duplicate_names:
            tag = "duplicate"
        elif is_bad_mod(mod):
            tag = "bad"
        else:
            tag = "good"
        mod_entries.append((tag, mod))


    priority = {"bad": 0, "duplicate": 1, "good": 2}

   
    mod_entries.sort(key=lambda x: (priority[x[0]], x[1]["name"].lower()))


    for tag, mod in mod_entries:
        tree.insert("", "end", values=(
            mod["name"],
            mod["size_mb"],
            mod["last_modified"],
            mod["path"],
            "Package" if mod["extension"] == ".package" else "TS4Script"
        ), tags=(tag,))


    package_count = sum(1 for m in mods if m["extension"] == ".package")
    script_count = sum(1 for m in mods if m["extension"] == ".ts4script")
    status_text.set(f"Total Mods: {len(mods)} | Packages: {package_count} | TS4Scripts: {script_count}")

def refresh_scan():
    if current_folder:
        scan_and_display(current_folder)
    else:
        messagebox.showinfo("No Folder Selected", "Please select a mods folder first.")

scan_button = tk.Button(button_frame, text="Scan Mods (Refresh)", command=refresh_scan)
scan_button.pack(side=tk.LEFT, padx=5)

def export_to_csv():
    messagebox.showinfo("Export", "Export to CSV feature not implemented yet.")

export_button = tk.Button(button_frame, text="Export to CSV", command=export_to_csv)
export_button.pack(side=tk.LEFT, padx=5)

exit_button = tk.Button(button_frame, text="Exit", command=root.destroy)
exit_button.pack(side=tk.RIGHT, padx=5)

status_text = tk.StringVar(value="No folder selected")
status_bar = tk.Label(root, textvariable=status_text, relief=tk.SUNKEN, anchor="w")
status_bar.pack(fill=tk.X, side=tk.BOTTOM)

menu = tk.Menu(root, tearoff=0)

def open_file_location():
    selected = tree.focus()
    if not selected:
        return
    path = tree.item(selected, "values")[3]
    if os.path.exists(path):
        if platform.system() == "Windows":
            subprocess.run(f'explorer /select,"{path}"')
        elif platform.system() == "Darwin":
            subprocess.run(["open", "-R", path])
        else:
            subprocess.run(["xdg-open", os.path.dirname(path)])
    else:
        messagebox.showerror("File not found", "The selected file does not exist.")

def delete_file():
    selected = tree.focus()
    if not selected:
        return
    path = tree.item(selected, "values")[3]
    confirm = messagebox.askyesno("Delete Confirmation", f"Are you sure you want to delete:\n{path}")
    if confirm:
        try:
            os.remove(path)
            messagebox.showinfo("Deleted", "File deleted successfully.")
            refresh_scan()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete file:\n{e}")

menu.add_command(label="Open File Location", command=open_file_location)
menu.add_command(label="Delete File", command=delete_file)

def show_menu(event):
    selected = tree.identify_row(event.y)
    if selected:
        tree.selection_set(selected)
        menu.post(event.x_root, event.y_root)

tree.bind("<Button-3>", show_menu) 
tree.bind("<Button-2>", show_menu) 

root.mainloop()

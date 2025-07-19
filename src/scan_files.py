from pathlib import Path
from datetime import datetime
from collections import defaultdict

def scan_mods_folder(mods_path):
    mods_path = Path(mods_path)
    if not mods_path.exists() or not mods_path.is_dir():
        print(f"Provided mods path does not exist or is not a directory: {mods_path}")
        return [], {}

    mod_data = []

    for file in mods_path.rglob("*"):
        if file.suffix.lower() in [".package", ".ts4script"]:
            stat = file.stat()
            file_info = {
                "name": file.name,
                "path": str(file),
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "last_modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %I:%M %p"),
                "extension": file.suffix.lower()
            }
            mod_data.append(file_info)

    duplicates_by_name = defaultdict(list)
    for mod in mod_data:
        duplicates_by_name[mod["name"]].append(mod["path"])

    duplicates_by_name = {name: paths for name, paths in duplicates_by_name.items() if len(paths) > 1}

    return mod_data, duplicates_by_name

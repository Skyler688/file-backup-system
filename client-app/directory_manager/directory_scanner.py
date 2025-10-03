import json
from pathlib import Path

# this function will scan through a target dir and map out the all of the dirs and files within it, 
# as well as usfule meta data like the type, size, and mtime.
# NOTE -> The mtime is very important and will be used to check if a file has changed or not,
# actual directory structer changes will be detected through comparing the saved json to a freash scan of the target.
def scan_dir(target_dir):
    path = Path(target_dir)
    node = {"name": path.name, "path": str(path), "type": "dir", "children": []}
    try:
        for entry in path.iterdir():
            try:
                if entry.is_dir():
                    node["children"].append(scan_dir(entry))
                else:
                    if entry.name != ".DS_Store":
                        stat = entry.stat()
                        node["children"].append({
                            "name": entry.name,
                            "path": str(entry),
                            "type": "file",
                            "size": stat.st_size,
                            "mtime": stat.st_mtime,
                        })
            except PermissionError:
                node["children"].append({
                    "name": entry.name,
                    "path": str(entry),
                    "type": "error",
                    "error": "permission"
                })
    except PermissionError:
        node["error"] = "permission"
    return node

def update_directory_map(target_dirs):
    with open("directory_manager/targets_map.json", "w") as targets_map:
        targets = {"targets": []}
        for target in target_dirs:
            targets["targets"].append(scan_dir(target))

        targets_map.write(json.dumps(targets, indent=2))    


def read_directory_map():
    retries = 3
    for _ in range(retries):
        try:
            with open("directory_manager/targets_map.json", "r") as targets_map:
                targets_map = json.load(targets_map)
                return targets_map
        except FileNotFoundError:
            update_directory_map([])
    print("ERROR -> Failed to create targets_map.json")            
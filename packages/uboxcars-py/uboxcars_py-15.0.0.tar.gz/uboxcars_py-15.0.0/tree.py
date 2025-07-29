import os

def print_tree(path, max_depth=2, current_depth=0, prefix=""):
    if current_depth > max_depth:
        return
    entries = sorted(os.listdir(path))
    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = "└── " if i == len(entries) - 1 else "├── "
        print(prefix + connector + entry)
        if os.path.isdir(full_path):
            extension = "    " if i == len(entries) - 1 else "│   "
            print_tree(full_path, max_depth, current_depth + 1, prefix + extension)

print_tree(".")

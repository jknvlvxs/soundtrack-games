import os

# Define the base directory
path = os.path.dirname(__file__)
base_dir = f"{path}/data/"

# Traverse the directory structure
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(root, file)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if ".7z" not in content and ".zip" not in content:
                os.remove(file_path)
                print(f"Deleted: {file_path}")

print("Completed the cleanup process.")

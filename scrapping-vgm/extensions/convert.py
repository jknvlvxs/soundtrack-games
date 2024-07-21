import json
import os

try:
    path = os.path.dirname(__file__)

    with open(f"{path}/can_convert.json", "r") as f:
        extensions = json.loads(f.read())

    extensions = [ext for ext in extensions if extensions[ext]]

    with open(f"{path}/convert.json", "w") as f:
        f.write(json.dumps(extensions))

    print("Extensions have been successfully written to convert.json")

except FileNotFoundError:
    print(f"File not found: {file_path}")

except Exception as e:
    print(f"An error occurred: {e}")

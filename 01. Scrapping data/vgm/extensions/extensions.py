import os
import json

try:
    path = os.path.dirname(__file__)
    
    with open(f"{path}/extensions.html", "r") as f:
        content = f.read()

    extensions = []

    for line in content.split("\n"):
        if '<span class="ext tag" data-ext="' in line:
            extension = line.split('data-ext="')[1].split('"')[0]
            extensions.append(extension)

    with open(f"{path}/extensions.json", "w") as f:
        f.write(json.dumps(extensions))

    print("Extensions have been successfully written to extensions.json")

except FileNotFoundError:
    print(f"File not found: {file_path}")

except Exception as e:
    print(f"An error occurred: {e}")

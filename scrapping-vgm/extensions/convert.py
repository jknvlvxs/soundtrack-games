import os
import json

path = os.path.dirname(__file__)

with open(f"{path}/extensions.json", "r") as json_file:
    extensions = json.load(json_file)

with open(f"{path}/ffmpeg/encoders.ffmpeg.txt", "r") as encoders_file:
    encoders_content = encoders_file.read()

filtered_extensions = [ext for ext in extensions if ext in encoders_content]

with open(f"{path}/convert.ffmpeg.json", "w") as output_file:
    json.dump(filtered_extensions, output_file, indent=4)

print("Filtered extensions have been saved to convert.ffmpeg.json")

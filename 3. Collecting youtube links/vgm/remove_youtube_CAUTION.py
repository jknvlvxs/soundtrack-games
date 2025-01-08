import json
import os

# Define the path to the metadata file
path = os.path.dirname(__file__)
data_file = os.path.join(path, "data.json")


def remove_youtube_attribute():
    try:
        # Load the data from metadata.json
        with open(data_file, "r", encoding="utf-8") as f:
            data_list = json.load(f)

        # Remove the "youtube" attribute from each object if it exists
        for obj in data_list:
            if "youtube" in obj:
                del obj["youtube"]

        # Save the modified data back to metadata.json
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=4)

        print("All 'youtube' attributes have been removed from each object.")

    except FileNotFoundError:
        print(f"File not found: {data_file}")

    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {data_file}")


remove_youtube_attribute()

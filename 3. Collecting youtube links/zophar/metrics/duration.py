import json
from datetime import timedelta


def parse_duration(duration):
    """
    Parse a YouTube duration string (HH:MM:SS or MM:SS) into a timedelta object.
    """
    parts = list(map(int, duration.split(":")))
    if len(parts) == 2:  # Format MM:SS
        return timedelta(minutes=parts[0], seconds=parts[1])
    elif len(parts) == 3:  # Format HH:MM:SS
        return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
    else:
        raise ValueError(f"Invalid duration format: {duration}")


def find_longest_duration(json_file):
    """
    Find and print the object with the longest YouTube duration from the JSON file.
    """
    with open(json_file, "r") as file:
        data = json.load(file)

    max_duration = timedelta()
    max_object = None

    for obj in data:
        try:
            duration = parse_duration(obj["youtube"]["duration"])
            if duration > max_duration:
                max_duration = duration
                max_object = obj
        except (KeyError, ValueError):
            print(f"Skipping invalid object: {obj['slug']}")

    if max_object:
        print("Object with the longest YouTube duration:")
        print(json.dumps(max_object, indent=4))
    else:
        print("No valid durations found in the data.")


# Replace 'data.json' with the path to your JSON file.
find_longest_duration("../metadata.json")

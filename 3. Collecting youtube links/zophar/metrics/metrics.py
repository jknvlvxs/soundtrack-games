import json
import os

path = os.path.dirname(__file__)
base_dir = os.path.join(path, "..")


def calculate_metrics(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data_list = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
        return

    total_objects = len(data_list)
    system_counts = {}
    total_size_mb = 0

    for obj in data_list:
        if obj.get("youtube") == None:
            total_objects -= 1
            continue

        system = obj.get("system")
        if system:
            if system in system_counts:
                system_counts[system] += 1
            else:
                system_counts[system] = 1

        total_size_mb += obj.get("size", 0)

    print(f"Total objects (.zip URL): {total_objects}")
    print(f"Total size (MB): {total_size_mb}\n")


def print_system_names(data_file):
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data_list = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {data_file}")
        return
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {data_file}")
        return

    system_counts = {}
    for obj in data_list:
        if obj.get("youtube") == None:
            continue

        system = obj.get("console")
        if system in system_counts:
            system_counts[system] += 1
        else:
            system_counts[system] = 1

    # order system_counts by value
    system_counts = dict(sorted(system_counts.items(), key=lambda item: item[1], reverse=True))

    print("Objects per system/console:")
    for system_name, count in system_counts.items():
        print(f"  {system_name}: {count}")


data_file = os.path.join(base_dir, "metadata.json")

calculate_metrics(data_file)
print_system_names(data_file)

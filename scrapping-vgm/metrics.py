import json
import os

path = os.path.dirname(__file__)
base_dir = os.path.join(path, "")
systems_dir = os.path.join(path, "systems")
systems_file = os.path.join(systems_dir, "systems.json")
names_file = os.path.join(systems_dir, "names.json")


def load_system_data():
    try:
        with open(systems_file, "r", encoding="utf-8") as f:
            system_codes = json.load(f)
        with open(names_file, "r", encoding="utf-8") as f:
            system_names = json.load(f)
    except FileNotFoundError:
        print(f"File not found. Check the path: {systems_file} or {names_file}")
        return {}, {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from files: {systems_file} or {names_file}")
        return {}, {}
    return system_codes, system_names


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
        system = obj.get("system")
        if system:
            if system in system_counts:
                system_counts[system] += 1
            else:
                system_counts[system] = 1

        total_size_mb += obj.get("size", 0)

    print(f"Total objects (.zip URL): {total_objects}\n")
    print(f"Total size (MB): {total_size_mb}\n")


def print_system_names(data_file):
    system_codes, system_names = load_system_data()
    if not system_codes or not system_names:
        return

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
        code = obj.get("system")
        if code and code in system_codes:
            index = system_codes.index(code)
            system_name = (
                system_names[index] if index < len(system_names) else "Unknown"
            )
            if system_name in system_counts:
                system_counts[system_name] += 1
            else:
                system_counts[system_name] = 1

    print("Objects per system/console:")
    for system_name, count in system_counts.items():
        print(f"  {system_name}: {count}")


data_file = os.path.join(base_dir, "data.json")

calculate_metrics(data_file)
print_system_names(data_file)

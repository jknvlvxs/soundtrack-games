import os
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from youtubesearchpython import VideosSearch

path = os.path.dirname(__file__)

data_dir = os.path.join(f"{path}/../1. Scrapping VGM Data", "data")
output_file = os.path.join(path, "data.json")

systems_dir = os.path.join(f"{path}/../1. Scrapping VGM Data", "systems")
systems_file = os.path.join(systems_dir, "systems.json")
names_file = os.path.join(systems_dir, "names.json")


def create_system_data():
    with open(systems_file, "r", encoding="utf-8") as f:
        system_codes = json.load(f)

    with open(names_file, "r", encoding="utf-8") as f:
        system_names = json.load(f)

    systems = {}
    for index, code in enumerate(system_codes):
        systems[code] = system_names[index]

    return systems


def find_date(text):
    pattern = r"\b\d{4}-\d{2}-\d{2}\b"

    match = re.search(pattern, text)

    if match:
        return match.group(0)
    else:
        return None


def convert_size_to_mb(size_str):
    if "MB" in size_str:
        size_value = float(size_str.replace("MB", "").strip())
    elif "GB" in size_str:
        size_value = float(size_str.replace("GB", "").strip()) * 1024
    elif "KB" in size_str:
        size_value = float(size_str.replace("KB", "").strip()) / 1024
    else:
        size_value = 0
    return int(size_value)


def convert_system_to_name(system_code):
    return Null


def dict_to_tuple(d):
    return tuple(sorted(d.items()))


def tuple_to_dict(t):
    return dict(t)


data_list = []
systems = create_system_data()

for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(root, file)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            soup = BeautifulSoup(content, "lxml")

            divs = soup.find_all("div", class_="url")

            for div in divs:
                a_tag = div.find("a")
                span_tag = div.find("span", class_="set-line")

                if a_tag and span_tag:
                    game_url = a_tag["href"]
                    file_size = span_tag.find("small", class_="info").text.strip()
                    name_tag = a_tag.text.strip()
                    system_code = span_tag.find("span", class_="sitetag").get(
                        "data-site"
                    )
                    date = find_date(name_tag)

                    if game_url == "" or date is None:
                        continue

                    obj = {
                        "url": game_url.replace(" ", "%20"),
                        "name": name_tag,
                        "size": convert_size_to_mb(file_size),
                        "date": date,
                        "system": systems.get(system_code, system_code),
                    }

                    data_list.append(obj)

object_set = set(dict_to_tuple(obj) for obj in data_list)
unique_objects = [tuple_to_dict(t) for t in object_set]

# order unique_objects by name
unique_objects = sorted(unique_objects, key=lambda item: item["name"])

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(unique_objects, f, indent=4, ensure_ascii=False)

print("Completed the generating data process.")

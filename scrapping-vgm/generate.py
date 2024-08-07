import os
import json
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

path = os.path.dirname(__file__)
base_dir = os.path.join(path, "data")
output_file = os.path.join(path, "data.json")


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


data_list = []

for root, dirs, files in os.walk(base_dir):
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
                    size_text = span_tag.find("small", class_="info").text.strip()
                    obj = {
                        "url": a_tag["href"].replace(" ", "%20"),
                        "name": a_tag.text.strip(),
                        "size": convert_size_to_mb(size_text),
                        "date": span_tag.find("small", class_="date").text.strip(),
                        "system": span_tag.find("span", class_="sitetag").get(
                            "data-site"
                        ),
                    }

                    if obj.get("url") != "":
                        data_list.append(obj)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data_list, f, indent=4, ensure_ascii=False)

print("Completed the generating data process.")

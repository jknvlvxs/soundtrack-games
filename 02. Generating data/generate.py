import os
import json
import re

from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from youtubesearchpython import VideosSearch

def format_release_date(release_date_tag):
    release_date_raw = release_date_tag.find("span", class_="infodata").text.strip() if release_date_tag else None
    
    if not release_date_raw:
        return None

    date_string = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', release_date_raw)

    try:
        return datetime.strptime(date_string, "%b %d, %Y").strftime("%d/%m/%Y")
    except ValueError:
        try:
            return datetime.strptime(f"1 {date_string}", "%d %b %Y").strftime("%d/%m/%Y")
        except ValueError:
            return None

path = os.path.dirname(__file__)

data_dir = os.path.join(f"{path}/../../1. Scrapping VGM Data/zophar", "data")
output_file = os.path.join(path, "data.json")

data_list = []
debug = ""

for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.endswith(f"{debug}.html"):
            file_path = os.path.join(root, file)
            
            game_slug = file_path.split("/")[-1].replace(".html", "")
            system_slug = file_path.split("/")[-2]

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            try:
                soup = BeautifulSoup(content, "lxml")

                # Extracting required data
                name = soup.find("div", id="music_info").find("h2").text.strip()
                # print(f"{name} | {file_path.split('/')[-1]}")

                # Extract cover URL if it exists
                cover_div = soup.find("div", id="music_cover")
                cover_img = cover_div.find("img") if cover_div else None
                cover = cover_img["src"] if cover_img else None

                # Extract console, emulator, and developer information
                info_tags = soup.find("div", id="music_info").find_all("p")
                console = None
                emulator = None
                developer = None

                for tag in info_tags:
                    info_name = tag.find("span", class_="infoname").text.strip()
                    info_data = tag.find("span", class_="infodata").text.strip()
                    if "Console" in info_name:
                        if "(" in info_data:
                            console, emulator = info_data.split(" (")
                            emulator = emulator.strip(")")
                        else:
                            console = info_data
                            emulator = None  # No emulator available
                    if "Developer" in info_name:
                        developer = info_data

                release_date_tag = next((tag for tag in info_tags if "Release date" in tag.find("span", class_="infoname").text.strip()), None)
                release_date = format_release_date(release_date_tag)

                mass_download = soup.find("div", id="mass_download").find("a")
                
                if not mass_download:
                    continue
                
                url = mass_download["href"]
                size_text = soup.find("div", id="mass_download").find("p").text.split("(")[-1].split(" ")[0]
                size = int(size_text) if size_text.isdigit() else 0

                # Form the final object
                obj = {
                    "slug": game_slug,
                    "name": name,
                    "console": console,
                    "system": system_slug,
                    "developer": developer,
                    "cover": cover,
                    "emulator": emulator,
                    "release_date": release_date,
                    "size": size,
                    "url": url,
                }
                
                # print(f"{obj}\n")
                data_list.append(obj)
            except Exception as e:
                print(f"Erro ao coletar arquivo: {file_path}")
                print(f"Erro: {e}\n")
                exit()

object_set = set(tuple(sorted(obj.items())) for obj in data_list)
unique_objects = [dict(t) for t in object_set]

# order unique_objects by name
unique_objects = sorted(unique_objects, key=lambda item: item["name"])

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(unique_objects, f, indent=4, ensure_ascii=False)

print("Completed the generating data process.")

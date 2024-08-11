import os
import json
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from youtubesearchpython import VideosSearch

path = os.path.dirname(__file__)
base_dir = os.path.join(f"{path}/../1. Scrapping VGM Data", "data")
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


def search_youtube(query):
    videosSearch = VideosSearch(query, limit=3)
    results = videosSearch.result()
    if "result" in results and len(results["result"]) > 0:
        first_video = results["result"][0]
        video_url = first_video["link"]
        video_channel = first_video["channel"]["name"]
        return video_url, video_channel
    return None, None


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
                    game_url = a_tag["href"]
                    file_size = span_tag.find("small", class_="info").text.strip()
                    game_name = a_tag.text.strip()

                    if(game_url == ""): continue

                    obj = {
                        "url": game_url.replace(" ", "%20"),
                        "name": game_name,
                        "size": convert_size_to_mb(file_size),
                        "date": span_tag.find("small", class_="date").text.strip(),
                        "system": span_tag.find("span", class_="sitetag").get("data-site"),
                    }

                    video_url, video_channel = search_youtube(f"{obj.name} {obj.system} full gameplay")

                    if(video_url is not None):
                        obj["youtube"] = {
                            "url": video_url,
                            "channel": video_channel
                        }

                    data_list.append(obj)


with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data_list, f, indent=4, ensure_ascii=False)

print("Completed the generating data process.")

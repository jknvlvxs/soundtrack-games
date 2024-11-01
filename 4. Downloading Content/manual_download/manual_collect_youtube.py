import json
import os
from youtubesearchpython import VideosSearch
import re

path = os.path.dirname(__file__)
base_dir = os.path.join(path, "")
data_file = os.path.join(path, "manual.json")

chunk_size = 100


def search_youtube(name, system, query=""):
    videosSearch = VideosSearch(f"{name} {system} {query}", limit=3)
    results = videosSearch.result()
    if "result" in results and len(results["result"]) > 0:
        first_video = results["result"][0]
        video_url = first_video["link"]
        video_channel = first_video["channel"]["name"]
        video_title = first_video["title"]
        duration = first_video["duration"]

        return video_url, video_channel, video_title, duration

    return None, None, None, None


def extract_name(name):
    # Remove content inside square brackets and parentheses
    cleaned_name = re.sub(r"\[.*?\]|\(.*?\)", "", name)
    # Strip any leading or trailing whitespace
    cleaned_name = (
        cleaned_name.strip()
        .replace(".7z", "")
        .replace(".zip", "")
        .replace("-", "")
        .replace(".", "")
    )
    return cleaned_name


def main():
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data_list = json.load(f)

        new_data_list = []

        for i in range(0, len(data_list), chunk_size):
            chunk = data_list[i : i + chunk_size]
            for index, obj in enumerate(chunk):
                print(
                    f"Searching for nº {i + index + 1} of {len(data_list)} ({int((i + index + 1) * 100/len(data_list))}%)"
                )

                # if "youtube" in obj:
                #     new_data_list.append(obj)
                #     continue

                name = extract_name(obj["name"].strip())
                system = obj["system"].strip()

                # target_channel = "World of Longplays"

                query = "longplay"

                video_url, video_channel, video_title, duration = search_youtube(
                    name, system, query
                )

                # if video_url is not None and video_channel == target_channel:
                if video_url is not None:
                    obj["youtube"] = {
                        "url": video_url,
                        "channel": video_channel,
                        "title": video_title,
                        "duration": duration,
                    }

                    new_data_list.append(obj)
                else:
                    with open(f"{base_dir}/not_found.log", "a") as f:
                        f.write(f"No video found for {name} {system}\n")

            with open(f"{base_dir}/links.json", "w", encoding="utf-8") as f:
                json.dump(new_data_list, f, indent=4)

    except FileNotFoundError as e:
        return print(f"File not found: {e}")

    except json.JSONDecodeError:
        return print(f"Error decoding JSON from file: {data_file}")


main()

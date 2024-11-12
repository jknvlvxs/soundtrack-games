import json
import os
from youtubesearchpython import VideosSearch
import re

path = os.path.dirname(__file__)
data_file = os.path.join(path, "metadata.json")
chunk_size = 100
target_channel = "World of Longplays"

def search_youtube(name, system, query=""):
    videosSearch = VideosSearch(f"{name} {system} {query}", limit=5)
    results = videosSearch.result()
    if "result" in results and len(results["result"]) > 0:
        selected_video = None

        for video in results["result"]:
            if video["channel"]["name"] == target_channel:
                selected_video = video
                break

        if selected_video is None:
            selected_video = results["result"][0]

        video_url = selected_video["link"]
        video_channel = selected_video["channel"]["name"]
        video_title = selected_video["title"]
        duration = selected_video["duration"]

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

        for i in range(0, len(data_list), chunk_size):
            chunk = data_list[i : i + chunk_size]
            for index, obj in enumerate(chunk):
                print(
                    f"Searching for nº {i + index + 1} of {len(data_list)} ({int((i + index + 1) * 100/len(data_list))}%)"
                )

                name = extract_name(obj["name"].strip())
                system = obj["system"].strip()
                query = "Longplay"

                video_url, video_channel, video_title, duration = search_youtube(
                    name, system, query
                )

                if video_url is not None:
                    obj["slug"] = obj["name"]
                    obj["name"] = name.strip()

                    obj["youtube"] = {
                        "url": video_url,
                        "channel": video_channel,
                        "title": video_title,
                        "duration": duration,
                    }
                else:
                    with open(os.path.join(path, "not_found.log"), "a") as f:
                        f.write(f"No video found for {name} {system}\n")

        # Save updated data_list back to the same file
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=4)

    except FileNotFoundError as e:
        print(f"File not found: {e}")

    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {data_file}")

main()

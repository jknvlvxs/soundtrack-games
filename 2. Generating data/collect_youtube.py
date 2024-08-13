import json
import os
from youtubesearchpython import VideosSearch

path = os.path.dirname(__file__)
base_dir = os.path.join(path, "")
data_file = os.path.join(base_dir, "data.json")

chunk_size = 100


def search_youtube(query):
    videosSearch = VideosSearch(query, limit=3)
    results = videosSearch.result()
    if "result" in results and len(results["result"]) > 0:
        first_video = results["result"][0]
        video_url = first_video["link"]
        video_channel = first_video["channel"]["name"]
        video_title = first_video["title"]
        duration = first_video["duration"]

        return video_url, video_channel, video_title, duration
    return None, None


def main():
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data_list = json.load(f)

        for i in range(0, len(data_list), chunk_size):
            chunk = data_list[i : i + chunk_size]
            for obj in chunk:
                name = obj["name"].strip().split(" (")[0]
                system = obj["system"].strip()

                query = f"{name} {system} Full Gameplay"
                video_url, video_channel, video_title, duration = search_youtube(query)

                if video_url is not None:
                    obj["youtube"] = {
                        "url": video_url,
                        "channel": video_channel,
                        "title": video_title,
                        "duration": duration,
                    }
                else:
                    print(f"No video found for {query}")

            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(data_list, f, indent=4)

            print(f"Processed {i + len(chunk)} of {len(data_list)}")

    except FileNotFoundError:
        return print(f"File not found: {data_file}")

    except json.JSONDecodeError:
        return print(f"Error decoding JSON from file: {data_file}")


main()

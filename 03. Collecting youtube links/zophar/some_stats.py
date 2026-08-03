import json
from datetime import timedelta
import numpy as np

META_DATA_PATH = "/home/felipe/Documents/Github/vmdb/03. Collecting youtube links/zophar/metadata.json"

with open(META_DATA_PATH, 'r') as f:
    meta_list = json.load(f)

total = 0
wolp = 0

# Mean gameplay duration
# Percentage of gameplays per channel

gameplay_durtaion_arr = []
total_video_files = 0
total_audio_files = 0
channels_dict = {}

for meta in meta_list:
    if meta["console"] == "Nintendo SNES":
        total += 1

        if meta.get("youtube"):
            channel_name = meta["youtube"]["channel"]
            if not channels_dict.get(channel_name):
                channels_dict[channel_name] = 1
            else:
                channels_dict[channel_name] += 1

            h = 0
            m = 0
            s = 0
            splited_time = meta["youtube"]["duration"].split(':')

            if len(splited_time) == 3:
                h, m, s = map(int, splited_time)
            elif len(splited_time) == 2:
                m, s = map(int, splited_time)
            elif len(splited_time) == 1:
                raise Exception("AAAAAAAAAAAAAAAAAAa")

            total_mins = timedelta(hours=h, minutes=m, seconds=s).total_seconds() / 60
            gameplay_durtaion_arr.append(total_mins)

            total_video_files += 1

        total_audio_files += meta["size"]


sorted_channels_dict = dict(sorted(channels_dict.items(), key=lambda item: item[1], reverse=True))

for channel in list(sorted_channels_dict)[:10]:
    proportion = sorted_channels_dict[channel]/total
    print(f"channel {channel} => {round(proportion*100, 3)}")

print(f"total channels {len(sorted_channels_dict.keys())}")

print(f"total video files = {total_video_files}")
print(f"total audio files = {total_audio_files}")

gameplay_durtaion_arr = np.array(gameplay_durtaion_arr)
print(f"mean gameplay duration = {gameplay_durtaion_arr.mean()}+-{gameplay_durtaion_arr.std()} mins")
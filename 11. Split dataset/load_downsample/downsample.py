import json
import pandas as pd

def downsample(df):
    return df


df = pd.read_csv("../get_videos_info/videos_info.csv")
filtered_df = downsample(df).sort_values(by=["game_id", "soundtrack"])
filtered_df.to_csv('videos_info.csv', index=False)

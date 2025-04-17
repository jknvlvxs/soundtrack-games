import json
import pandas as pd

selected_segments = set()

with open('selected_videos.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line)
        video_path = data['video_description_path']
        segment = video_path.split('/')[-1]  # Get the filename (e.g., 3-ninjas-kick-back_00005.mp4)
        selected_segments.add(segment)

df = pd.read_csv('videos_info.csv')
filtered_df = df[df['segment'].isin(selected_segments)]

filtered_df.to_csv('selected_videos_info.csv', index=False)

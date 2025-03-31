############################################################################################################################
# Select videos descriptions according with the file mapping in order to have at least one video description per soundtrack
############################################################################################################################
import os
from copy import deepcopy
import json

from tqdm import tqdm

ROOT = '/home/es119256/datasets/vmdb/nintendo-snes-spc'
SAVE_PATH = '/home/es119256/datasets/vmdb/selected_videos.jsonl'

MIN_TEMP_STRIDE = 60*2 # Minimum temporal stride to retrieve another video description for the same soundtrack

def select_videos_with_temp_stride(temp_stide:int, videos:list[str]):
    """
        Select videos spaced by a minimum temporal stride
        Last 5 digits in the video's name times 10 identify it's beggining in seconds (in relation to the whole gameplay)
    """
    selected_videos = []

    last_selected_time = -float('inf')
    for video in videos:
        current_time = (int(video[-9:-4]) -1) *10 # -1 because the first video is 00001, so now we start from 0s

        if current_time >= last_selected_time + temp_stide:
            selected_videos.append(video)
            last_selected_time = current_time

    return selected_videos

def test_select_videos_with_temp_stride():
    videos = []
    for i in range(1, 200, 1):
        videos.append(f"video_{i:05d}.mp4")

    selected = select_videos_with_temp_stride(MIN_TEMP_STRIDE, videos)
    print(selected)

def save_videos(videos:list[tuple[str, str]]):
    with open(SAVE_PATH, 'a') as jsonl_file:
        for video in videos:
            video_description_path, music_description_path = video
            json.dump(
                {
                    'video_description_path': video_description_path,
                    'music_description_path': music_description_path
                },
                jsonl_file
            )
            jsonl_file.write('\n')

if __name__ == '__main__':
    files = []

    for game_folder in tqdm(sorted(os.listdir(ROOT))):
        videos_folder = os.path.join(ROOT, game_folder, 'videos')
        videos_descriptions_folder = os.path.join(ROOT, game_folder, 'videos_descriptions')

        for video_or_folder in sorted(os.listdir(videos_folder)):
            # If it isn't a video, it will be a folder of videos with the name of the soundtrack identified in those videos
            video_or_folder_path = os.path.join(videos_folder, video_or_folder)

            # Loop if it is a folder. We're not interested in videos outside soundtrack folders (videos not mapped to any soundtrack)
            if os.path.isdir(video_or_folder_path):
                videos_in_folder = sorted(os.listdir(video_or_folder_path))
                selected_videos = select_videos_with_temp_stride(MIN_TEMP_STRIDE, videos_in_folder)

                for video_in_folder in selected_videos:
                    video_in_folder_path = os.path.join(video_or_folder_path, video_in_folder)
                    result_txt_path = os.path.join(videos_descriptions_folder, video_in_folder)[:-3]+"txt"

                    files.append((video_in_folder_path, result_txt_path))

        # Sort the videos
        sort_files = deepcopy(files)
        for idx in range(len(sort_files)):
            sort_files[idx] = sort_files[idx][0].split('/')[-1]

        files = [val for _, val in sorted(zip(sort_files, files))]

    save_videos(files)
    print(len(files))
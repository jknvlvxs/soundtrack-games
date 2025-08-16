import os
import pandas as pd
from tqdm import tqdm
from math import isnan

DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-back/vmdb/nintendo-snes-spc" 

IN_CONF = "input_confidence"
FINGER_CONF = "fingerprinted_confidence"

DRY_RUN = True
VERBOSE = True

IN_CONF_THRESHOLD = 0.0
FINGER_CONF_THRESHOLD = 0.01

def unmap_video(from_path:str, to_path:str):
    # Move video out from videos/soundtrack_XXXX to videos/ folder
    if not DRY_RUN:
        os.rename(from_path, to_path)

        if VERBOSE:
            from_path = '/'.join(from_path.split("/")[-2:])
            to_path = '/'.join(to_path.split("/")[-2:])
            print(f"Moved {from_path} -------> {to_path}\n")

def unmap_all_videos(videos_path:str):
    for video_or_folder in os.listdir(videos_path):
        video_or_folder_path = os.path.join(videos_path, video_or_folder)

        # if it is mapped (inside a soundtrack folder), unmap it
        if os.path.isdir(video_or_folder_path):
            sdtk_path = video_or_folder_path

            for video_name in os.listdir(sdtk_path):
                video_path = os.path.join(sdtk_path, video_name)
                new_video_path = os.path.join(videos_path, video_name)

                unmap_video(video_path, new_video_path)

def main():
    total_videos = 0
    removed_videos = 0

    games_folders = sorted(os.listdir(DATASET_ROOT))

    for game_folder in tqdm(games_folders, total=len(games_folders), desc="Games Folders"):
        game_folder_path = os.path.join(DATASET_ROOT, game_folder) 
        videos_path = os.path.join(game_folder_path, 'videos')
        dejavu_csv_path = os.path.join(DATASET_ROOT, game_folder, "mapping_log.csv")

        # There are games with no videos and no mapping_log
        # There is yokoyama-mitsuteru-sangokushi with videos and no mapping_log
        # Thre is earthbound with no videos and an empty mapping_log
        # If there is no mapping_log we can't say anything about the Dejavu's confidence, 
        # so if there are videos we should unmap them right away
        if not os.path.exists(dejavu_csv_path):
            unmap_all_videos(videos_path)
            continue

        dejavu_df = pd.read_csv(dejavu_csv_path)

        # If there are no rows in the mapping_csv and there are videos, 
        # we should also unmap them right awaydejavu_df
        if len(dejavu_df) == 0:
            unmap_all_videos(videos_path)
            continue

        for _, video_row in dejavu_df.iterrows():
            total_videos += 1

            video, soundtrack, input_confidence, fingerprinted_confidence = video_row
            input_confidence = 0.0 if isnan(input_confidence) else input_confidence
            fingerprinted_confidence = 0.0 if isnan(fingerprinted_confidence) else fingerprinted_confidence

            # Continue if we don't have to remove this video
            confidence_is_higher = input_confidence >= IN_CONF_THRESHOLD and fingerprinted_confidence >= FINGER_CONF_THRESHOLD

            new_video_path = os.path.join(DATASET_ROOT, game_folder, 'videos', video)
            already_unmaped = not isinstance(soundtrack, str) or os.path.exists(new_video_path)

            if confidence_is_higher or already_unmaped:
                continue

            video_path = os.path.join(DATASET_ROOT, game_folder, 'videos', soundtrack, video)

            unmap_video(video_path, new_video_path)

            removed_videos += 1

    lost = 0 
    if total_videos > 0:
        lost = (removed_videos/total_videos)*100
    print(f"Total videos: {total_videos}, Removed videos: {removed_videos}, Lost: {lost}%")

if __name__ == "__main__":
    main()
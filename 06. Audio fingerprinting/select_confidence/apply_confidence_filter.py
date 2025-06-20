import os
import pandas as pd
from tqdm import tqdm
from math import isnan

DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-back/vmdb/nintendo-snes-spc" 

IN_CONF = "input_confidence"
FINGER_CONF = "fingerprinted_confidence"

DRY_RUN = False

IN_CONF_THRESHOLD = 0.0
FINGER_CONF_THRESHOLD = 0.01

def main():
    total_videos = 0
    removed_videos = 0

    games_folders = sorted(os.listdir(DATASET_ROOT))

    for game_folder in tqdm(games_folders, total=len(games_folders), desc="Games Folders"):
        dejavu_csv_path = os.path.join(DATASET_ROOT, game_folder, "mapping_log.csv")

        if not os.path.exists(dejavu_csv_path):
            continue

        dejavu_df = pd.read_csv(dejavu_csv_path)

        for _, video_row in dejavu_df.iterrows():
            total_videos += 1

            video, soundtrack, input_confidence, fingerprinted_confidence = video_row
            input_confidence = 0.0 if isnan(input_confidence) else input_confidence
            fingerprinted_confidence = 0.0 if isnan(fingerprinted_confidence) else fingerprinted_confidence

            # Continue if we don't have to remove this video
            confidence_is_higher = input_confidence >= IN_CONF_THRESHOLD and fingerprinted_confidence >= FINGER_CONF_THRESHOLD
            already_unmaped = not isinstance(soundtrack, str)

            if confidence_is_higher or already_unmaped:
                continue

            removed_videos += 1

            # Move video out from the videos/soundtrack_XXXX folder so that it is seem as unmapped
            video_path = os.path.join(DATASET_ROOT, game_folder, 'videos', soundtrack, video)
            new_video_path = os.path.join(DATASET_ROOT, game_folder, 'videos', video)

            if not DRY_RUN:
                #print(f"Moved {video}\nfrom: {video_path}\nto: {new_video_path}\n")
                os.rename(video_path, new_video_path)

    print(f"Total videos: {total_videos}, Removed videos: {removed_videos}, Lost: {(removed_videos/total_videos)*100}%")

if __name__ == "__main__":
    main()
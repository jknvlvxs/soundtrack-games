# %% 
import os
import subprocess as sp
import pandas as pd

DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-back/vmdb/nintendo-snes-spc" 

GAME = "brunswick-world-tournament-of-champions"

IN_CONF = "input_confidence"
FINGER_CONF = "fingerprinted_confidence"

def main():
    game_folder = os.path.join(DATASET_ROOT, GAME)

    dejavu_csv_path = os.path.join(game_folder, "mapping_log.csv")
    dejavu_df = pd.read_csv(dejavu_csv_path)

    # map the FINGER_CONF column to FINGER_CONF * 10
    dejavu_df[FINGER_CONF] *= 10

    # sum confidences and sort by this sum
    dejavu_df["confidence_sum"] = dejavu_df[IN_CONF] + dejavu_df[FINGER_CONF]
    dejavu_df = dejavu_df.sort_values("confidence_sum")

    for _, video_row in dejavu_df.iterrows():
        video, soundtrack, input_confidence, fingerprinted_confidence, confidence_sum = video_row

        video_path = os.path.join(game_folder, 'videos', soundtrack, video)
        mapped_to_sdtk = os.path.join(game_folder, 'soundtracks', soundtrack+'.mp3')

        print(video)
        print(input_confidence, fingerprinted_confidence, confidence_sum)
        print(video_path)
        sp.Popen(["vlc", video_path]) # had to run on linux terminal outside vs code
        print(mapped_to_sdtk)
        sp.Popen(["vlc", mapped_to_sdtk]) # had to run on linux terminal outside vs code
        input()

if __name__ == "__main__":
    main()

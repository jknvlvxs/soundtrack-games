# %% 
import os
import subprocess as sp
import pandas as pd

DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-back/vmdb/nintendo-snes-spc" 

GAME = "go-go-ackman"

IN_CONF = "input_confidence"
FINGER_CONF = "fingerprinted_confidence"

SKIP = 0

def main():
    game_folder = os.path.join(DATASET_ROOT, GAME)

    dejavu_csv_path = os.path.join(game_folder, "mapping_log.csv")
    dejavu_df = pd.read_csv(dejavu_csv_path)
    dejavu_df = dejavu_df.fillna(0)

    # map the FINGER_CONF column to FINGER_CONF * 10
    dejavu_df[FINGER_CONF] *= 10

    # sum confidences and sort by this sum
    dejavu_df["confidence_sum"] = dejavu_df[IN_CONF] + dejavu_df[FINGER_CONF]
    dejavu_df = dejavu_df.sort_values("confidence_sum", ascending=False)

    for idx, row in enumerate(dejavu_df.iterrows()):
        _, video_row = row
        video, soundtrack, input_confidence, fingerprinted_confidence, confidence_sum = video_row

        if soundtrack == 0 or idx < SKIP:
            continue

        video_path = os.path.join(game_folder, 'videos', soundtrack, video)
        mapped_to_sdtk = os.path.join(game_folder, 'soundtracks', soundtrack+'.mp3')

        sp.run(["clear"], shell=True, check=True)
        print('INDEX:', idx+1, '\n')

        print(video)
        print('IN CONF', input_confidence, 'FING CONF', fingerprinted_confidence, 'TOTAL CONF', confidence_sum, '\n')

        print(video_path, '\n')
        video_popen = sp.Popen(["vlc", video_path]) # had to run on linux terminal outside vs code
        print(mapped_to_sdtk)
        sdtk_popen = sp.Popen(["vlc", mapped_to_sdtk]) # had to run on linux terminal outside vs code

        input()
        video_popen.terminate()
        sdtk_popen.terminate()

if __name__ == "__main__":
    main()

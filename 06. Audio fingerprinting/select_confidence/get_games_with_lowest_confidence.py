# %% 
import os
import pandas as pd

DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-back/vmdb/nintendo-snes-spc" 

IN_CONF = "input_confidence"
FINGER_CONF = "fingerprinted_confidence"

def main():
    total_game_confidence = []
    game_name = []

    for game_folder in sorted(os.listdir(DATASET_ROOT)):
        dejavu_csv_path = os.path.join(DATASET_ROOT, game_folder, "mapping_log.csv")

        if not os.path.exists(dejavu_csv_path):
            continue

        dejavu_df = pd.read_csv(dejavu_csv_path)

        dejavu_inf_conf = dejavu_df[IN_CONF].mean()
        dejavu_finger_conf = dejavu_df[FINGER_CONF].mean() *10
        confidence_sum = dejavu_inf_conf + dejavu_finger_conf

        total_game_confidence.append(confidence_sum)
        game_name.append(game_folder)

    # sort game name according to total_game_confidence
    sorted_keys = range(len(total_game_confidence))

    sorted_keys = sorted(sorted_keys, key=lambda k: total_game_confidence[k])
    sorted_names = [game_name[k] for k in sorted_keys]

    sorted_total_game_confidence = sorted(total_game_confidence)

    for idx in range(20):
        print(f"game {sorted_names[idx]}, confidence {round(sorted_total_game_confidence[idx], 2)}")

if __name__ == "__main__":
    main()
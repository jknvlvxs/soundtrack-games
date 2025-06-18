import os
import pandas as pd

DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-back/vmdb/nintendo-snes-spc" 

IN_CONF = "input_confidence"
FINGER_CONF = "fingerprinted_confidence"

THRESHOLD = 0.2

def main():
    confidence_dict_list = []
    skiped = 0

    for game_folder in sorted(os.listdir(DATASET_ROOT)):
        dejavu_csv_path = os.path.join(DATASET_ROOT, game_folder, "mapping_log.csv")

        if not os.path.exists(dejavu_csv_path):
            continue

        dejavu_df = pd.read_csv(dejavu_csv_path)
        dejavu_df = dejavu_df.fillna(0)

        dejavu_inf_conf = dejavu_df[IN_CONF].mean()
        dejavu_finger_conf = dejavu_df[FINGER_CONF].mean() *10
        confidence_sum = dejavu_inf_conf + dejavu_finger_conf

        if confidence_sum < THRESHOLD:
            skiped += 1
            continue

        confidence_dict_list.append(
            {
                "confidence": confidence_sum,
                "name": game_folder,
                "df": dejavu_df
            }
        )

    # sort game name according to total_game_confidence
    confidence_dict_list = sorted(confidence_dict_list, key=lambda x: x['confidence'])

    print(f"Skiped: {skiped}")
    for idx in range(0,100):
        confidence_dict = confidence_dict_list[idx]
        print(f"{idx+1} | game {confidence_dict['name']} | confidence {confidence_dict['confidence']:.2}")

if __name__ == "__main__":
    main()
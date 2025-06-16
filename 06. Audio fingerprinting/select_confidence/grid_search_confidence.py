# %% 
import os
import json
import itertools
from typing import Any

import pandas as pd
from tqdm import tqdm

DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-mock" 
VIDEOS_GT_JSON = "./videos_gt.json" # ground truth

IN_CONF = "input_confidence"
FINGER_CONF = "fingerprinted_confidence"

START = 0.0
STOP = 3.0
STEP = 0.01

def run_with_confidence(videos_gt_dict, in_conf, finger_conf) -> tuple[int, int, int]:
    """
        Run search for every game with given input and finguerprint confidences.

        Explanation of this metrics:
            Input confidence is the percentage regarding hashes matched vs hashes from the input: hashes_matched / queried_hashes.
            Fingerprinted confidence is the percentage regarding hashes matched vs hashes fingerprinted from a song in the db: hashes_matched / song_hashes.

        Args:
            `videos_gt_dict`: dictionary with the ground truth labels for the videos
            `in_conf`: inferior threshold for input confidence 
            `finguer_conf`: inferior threshold for finguerprint confidence

        Returns:
            `global_count`: number of evaluated videos

            `global_correct`: number of videos correctly evaluated with the given `in_conf` and `finger_conf`

            `global_lost`: number of videos lost, because the dejavu confidences were lower than the given `in_conf` and `finger_conf`
    """
    global_count = 0
    global_correct = 0
    global_lost = 0

    for game in videos_gt_dict:
        dejavu_csv_path = os.path.join(DATASET_ROOT, game, "mapping_log.csv")
        dejavu_df = pd.read_csv(dejavu_csv_path)

        mp4s = videos_gt_dict[game]["mp4"]
        gt_clss = videos_gt_dict[game]["class"]

        game_count = 0
        game_correct = 0

        for mp4, gt_cls in zip(mp4s, gt_clss):
            dejavu_mp4_info = dejavu_df[dejavu_df['video'] == f"{game}_{mp4}.mp4"]

            dejavu_inf_conf = dejavu_mp4_info[IN_CONF].to_list()[0]
            dejavu_finger_conf = dejavu_mp4_info[FINGER_CONF].to_list()[0]

            if dejavu_inf_conf >= in_conf and dejavu_finger_conf >= finger_conf:
                dejavu_sdtk = dejavu_mp4_info["soundtrack"].to_list()[0]
            else:
                dejavu_sdtk = "soundtrack_NaN"
                global_lost += 1

            #tqdm.write(f"game:{game}, video:{dejavu_mp4_info['video'].to_list()[0]}, dejavu_sdtk:{dejavu_sdtk}, gt_cls:{gt_cls}, dejavu_inf_conf: {dejavu_inf_conf}, dejavu_finger_conf: {dejavu_finger_conf}")

            game_count += 1
            game_correct = game_correct + 1 if dejavu_sdtk == f"soundtrack_{gt_cls}" else game_correct
            #tqdm.write(f"correnct: {game_correct}\n")

        global_count += game_count
        global_correct += game_correct

    return global_count, global_correct, global_lost

def main():
    videos_gt_dict:dict[str, Any]
    with open(VIDEOS_GT_JSON, 'r') as f:
        videos_gt_dict = json.load(f)

    in_conf_possibilities = itertools.takewhile(lambda x: x < STOP, itertools.count(START, STEP))
    finger_conf_possibilities = itertools.takewhile(lambda x: x < STOP, itertools.count(START, STEP))
    all_possibilities = itertools.product(in_conf_possibilities, finger_conf_possibilities)

    best_in_conf = 0
    best_finger_conf = 0
    best_acc = 0
    for current_step in tqdm(all_possibilities, total=90_601):
        current_in_conf, current_finger_conf = current_step
        current_in_conf, current_finger_conf = round(current_in_conf, 2), round(current_finger_conf, 2)

        # Run with current_step for every game
        total_count, correct_count, lost_count = run_with_confidence(videos_gt_dict, current_in_conf, current_finger_conf )

        acc = round(correct_count / total_count, 2)
        lost_percentage = round(lost_count / total_count, 2)

        if acc > best_acc:
            tqdm.write(f"NEW BEST ACC. For ({current_in_conf}, {current_finger_conf}), acc is {acc*100}% & lost {lost_percentage*100}% of the videos. Previous was ({best_in_conf}, {best_finger_conf}) with acc {best_acc*100}%")
            best_acc = acc
            best_in_conf = current_in_conf
            best_finger_conf = current_finger_conf

if __name__ == "__main__":
    main()
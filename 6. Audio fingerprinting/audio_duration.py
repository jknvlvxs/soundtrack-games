import os
import json
import argparse
import traceback
import sys
import os
from mutagen.mp3 import MP3
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="dejavu.py")
    # parser.add_argument("--dataset_root", type=str, default="../5. Database/", help="path for the dataset games folder")
    parser.add_argument("--dataset_root", type=str, default="/app/dataset/", help="path for the dataset games folder")
    parser.add_argument("--console", type=str, default="nintendo-snes-spc", help="selected console")
    args = parser.parse_args()

    dataset_path = args.dataset_root + args.console

    games_folders = sorted(os.listdir(dataset_path))
    n_games = len(games_folders)

    durations = []

    for game in tqdm(games_folders):
        soundtracks_path = os.path.join(dataset_path, game, "soundtracks")
        game_soundtracks = sorted(os.listdir(soundtracks_path))

        for soundtrack in game_soundtracks:
            if soundtrack.startswith("soundtrack_") and soundtrack.endswith(".mp3"):
                file_path = os.path.join(soundtracks_path, soundtrack)
                try:
                    durations.append(MP3(file_path).info.length)
                except Exception as e:
                    print(f"Erro ao processar {file_path}: {e}")
                    continue

    # Export durations to a JSON
    with open("durations.json", "w") as f:
        json.dump(durations, f)

import os
import argparse
import csv

from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='get_videos_info.py')
    parser.add_argument("--dataset_root", type=str, default="/home/es119256/dados/datasets/vmdb_3/", help="path for the dataset games folder")
    parser.add_argument("--console", type=str, default="nintendo-snes-spc", help="selected console")
    args = parser.parse_args()

    dataset_path = args.dataset_root + args.console

    games_folders = sorted(os.listdir(dataset_path))

    with open("deepseek_genres.csv", mode="r") as csv_file:
        deepseek_genres = {row["game_id"]: row["genre"] for row in csv.DictReader(csv_file)}

    output_csv_path = os.path.join("videos_info.csv")
    with open(output_csv_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["index", "game_id", "soundtrack", "segment", "genre"])

        index = 1

        for game in tqdm(games_folders, total=len(games_folders)):
            video_folder_path = os.path.join(dataset_path, game, "videos")

            if not os.path.isdir(video_folder_path):
                continue

            soundtrack_dirs = sorted([d for d in os.listdir(video_folder_path) if os.path.isdir(os.path.join(video_folder_path, d)) and d.startswith("soundtrack_")])
            for subfolder in soundtrack_dirs:
                subfolder_path = os.path.join(video_folder_path, subfolder)
                game_videos = sorted(os.listdir(subfolder_path))

                tqdm.write(f"Mapping videos for {game}")

                for video in game_videos:
                    genre = deepseek_genres.get(game, "unknown")

                    with open(output_csv_path, mode="a", newline="") as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow([index, game, subfolder, video, genre])
                        index = index + 1

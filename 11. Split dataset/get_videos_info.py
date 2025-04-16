import os
import argparse
import csv

from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='get_videos_info.py')
    parser.add_argument('--dataset_root', type=str, default="../5. Database/nintendo-snes-spc/", help="path for the dataset games folder")
    args = parser.parse_args()

    games_folders = sorted(os.listdir(args.dataset_root))

    with open("deepseek_genres.csv", mode="r") as csv_file:
        deepseek_genres = {row["game_id"]: row["genre"] for row in csv.DictReader(csv_file)}

    output_csv_path = os.path.join("videos_info.csv")
    with open(output_csv_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["index", "game_id", "segment", "genre"])

    for game in tqdm(games_folders, total=len(games_folders)):
        video_folder_path = os.path.join(args.dataset_root, game, 'videos')
        game_videos = sorted(os.listdir(video_folder_path))

        tqdm.write(f"Mapping videos for {game}")

        for index, video in enumerate(game_videos, start=1):
            genre = deepseek_genres.get(game, "unknown")

            with open(output_csv_path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([index, game, video, genre])

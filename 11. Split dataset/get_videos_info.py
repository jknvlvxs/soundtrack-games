import os
import argparse
import csv

from tqdm import tqdm

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='get_videos_info.py')
    parser.add_argument('--dataset_root', type=str, default="../5. Database/nintendo-snes-spc/", help="path for the dataset games folder")
    args = parser.parse_args()

    games_folders = sorted(os.listdir(args.dataset_root))

    for game in tqdm(games_folders, total=len(games_folders)):
        video_folder_path = os.path.join(args.dataset_root, game, 'videos')
        game_videos = sorted(os.listdir(video_folder_path))

        tqdm.write(f"Mapping videos for {game}")

        deepseek_genres_path = os.path.join("deepseek_genres.csv")
        deepseek_genres = {}

        if os.path.exists(deepseek_genres_path):
            with open(deepseek_genres_path, mode="r") as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    deepseek_genres[row["game_id"]] = row["genre"]
        else:
            raise FileNotFoundError(f"{deepseek_genres_path} not found.")

        genre = deepseek_genres[game] if game in deepseek_genres else "unknown"

        output_csv_path = os.path.join("videos_info.csv")

        with open(output_csv_path, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["index", "game_id", "segment", "genre"])

        for index, video in enumerate(game_videos, start=1):
            video_path = os.path.join(video_folder_path, video)

            with open(output_csv_path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([index, game, video, genre])

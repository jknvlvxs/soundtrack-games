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
        
        for video in game_videos:
            video_path = os.path.join(video_folder_path, video)

            output_csv_path = os.path.join('videos_info.csv')

            if not os.path.exists(output_csv_path):
                with open(output_csv_path, mode='w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(['index', 'game_id', 'segment', 'genre'])

            with open(output_csv_path, mode='a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                index = sum(1 for _ in open(output_csv_path))  # Calculate the current index
                writer.writerow([index, game, video])
            
            
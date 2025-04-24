import os 
import pandas as pd

SPLIT_TXTS = "../11. Split dataset/3. split/splits"
VIDEOS_CSV = "../11. Split dataset/2. downsample/videos_info.csv"
DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-back/vmdb/nintendo-snes-spc"

def get_split() -> dict[str, list[str]]:
    split_games = {
        'train': [], 
        'eval': [], 
        'test': []
    }

    for split in split_games:
        split_path = os.path.join(SPLIT_TXTS, split+'.txt')

        with open(split_path, 'r') as f:
            split_games[split] = f.read().split('\n')

    return split_games

def main():
    split_dict = get_split()
    videos_csv = pd.read_csv(VIDEOS_CSV)

    # Create folder where the shortcuts will go
    # Loop the dataset copying according to the split and videos_csv
    # Create shortcuts for the selected soundtracks and json
    # json should contain the path to the video and the video description
    # json name shoud be soundtrack_name_001, soundtrack_name_002, etc...

if __name__ == "__main__":
    main()
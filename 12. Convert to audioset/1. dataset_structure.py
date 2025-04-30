###########################################################################################################
# To put our dataset in the format https://github.com/facebookresearch/audiocraft/tree/main/dataset/example
###########################################################################################################
import os
import json
import argparse

from tqdm import tqdm
import pandas as pd
import ffmpeg

SPLIT_TXTS = "../11. Split dataset/3. split/splits"
VIDEOS_CSV = "../11. Split dataset/2. downsample/videos_info.csv"

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

def convert_game(dataset_root:str, split_path:str, game:str, videos_csv:pd.DataFrame):
    """
        Audiocraft dataset have the format

            my_dataset/split
                |_audio_001.mp3
                |_audio_001.json

        The audio will be the game soundtrack. The json will contain the videos descriptions of
        video segments mapped to the corresponding soundtrack and the path to the segment's mp4.

        We'll use videos_csv to get the selected segments and create links for the soundtracks
        instead of copying the whole audio.
    """
    game_df = videos_csv[videos_csv["game_id"] == game]
    game_soundtracks:list[str] = game_df["soundtrack"].unique()

    for soundtrack in game_soundtracks:
        soundtrack_df = game_df[game_df['soundtrack'] == soundtrack]

        # Soundtrack original and target paths
        soundtrack_orig_path = os.path.join(dataset_root, game, 'soundtracks', soundtrack+'.mp3')

        soundtrack_tgt_file = f"{game}_{soundtrack}.mp3"
        soundtrack_tgt_path= os.path.join(split_path, soundtrack_tgt_file)
        soundtrack_json_path = soundtrack_tgt_path[:-3]+'json'

        if os.path.exists(soundtrack_tgt_path) and os.path.exists(soundtrack_json_path):
            continue

        # Get soundctrack meta
        try:
            probe:dict = ffmpeg.probe(soundtrack_orig_path)
        except Exception as e:
            print(f"Erro in ffmpeg.prob for game {game} in {soundtrack}")
            continue
            # TODO the soundtracks that failed probe simply do not exist:
            # lufia-ii-rise-of-the-sinistrals-[lufia]-1994 in soundtrack_0059
            # lufia-ii-rise-of-the-sinistrals-[lufia]-1994 in soundtrack_0060
            # lufia-ii-rise-of-the-sinistrals-[lufia]-1994 in soundtrack_0062

            # Clearly this is a problem with mapping, because in the game names
            # lufia-ii-rise-of-the-sinistrals-[lufia]
            # lufia-ii-rise-of-the-sinistrals-[lufia]-1994 TODO: throw this game on the trash
            # The dejavu step the both would be changed to 
            # lufia-ii-rise-of-the-sinistrals
            # because there is a .split("[")[0] in mapping.py and drop_database.py

        # Create link for the soundtrack in the converted dataset
        if not os.path.exists(soundtrack_tgt_path): # because the link can exist w/o the json
            os.symlink(soundtrack_orig_path, soundtrack_tgt_path)

        # Loop soundtrack seguiments to get all the descriptions and mp4 paths
        segments_paths = []
        segments_descriptions = []
        for _, row in soundtrack_df.iterrows():
            soundtrack, segment = row['soundtrack'], row['segment']

            # Oringinal paths
            segment_orig_path = os.path.join(dataset_root, game, 'videos', soundtrack, segment)
            description_orig_path = os.path.join(dataset_root, game, 'videos_descriptions', segment[:-3]+'txt')

            # Read description
            with open(description_orig_path, 'r') as f:
                description = f.read()

            segments_paths.append(segment_orig_path)
            segments_descriptions.append(description)

        soundtrack_json = {
            "key": "", 
            "artist": '', #probe['format'].get('tags', {}).get('artist', ''),
            "sample_rate": probe['streams'][0]['sample_rate'],
            "file_extension": probe['streams'][0]['codec_name'], 
            #"description": this field is now replaced by segments_paths/segments_descriptions
            "keywords": "",
            "duration": probe['streams'][0]['duration'],
            "bpm": "", 
            "genre": "", 
            "title": '', #probe['format'].get('tags', {}).get('title', ''),
            "name": soundtrack_tgt_file, 
            "instrument": "",
            "moods": [],
            # New tags that are not part of the MusicGen examples
            "year": '', #probe['format'].get('tags', {}).get('copyright', ''),
            "segments_paths": segments_paths,
            "segments_descriptions": segments_descriptions
        }
        # TODO check on the paper how this keys of the dictionary are used

        with open(soundtrack_json_path, 'w') as f:
            json.dump(soundtrack_json, f, indent=4)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='1. dataset_structure.py')
    parser.add_argument('--original_dataset', type=str, default="/app/dataset/nintendo-snes-spc", help="path for the snes mvdb dataset games folder")
    parser.add_argument('--converted_dataset', type=str, default="/app/audiocraft/dataset", help="path to audiocraft/dataset where the converted dataset will be")

    args = parser.parse_args()
    original_dataset = args.original_dataset
    converted_dataset = os.path.join(args.converted_dataset, 'snes_mvdb')

    split_dict = get_split()
    segments_df = pd.read_csv(VIDEOS_CSV)

    # Create folder where the links will go
    if not os.path.exists(converted_dataset):
        os.makedirs(converted_dataset)

    # Loop the dataset according to the split
    for split, games in split_dict.items():
        split_path = os.path.join(converted_dataset, split)

        if not os.path.exists(split_path):
            os.mkdir(split_path)

        for game in tqdm(games, desc=split):
            convert_game(original_dataset, split_path, game, segments_df)

if __name__ == "__main__":
    main()
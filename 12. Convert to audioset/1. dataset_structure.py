###########################################################################################################
# To put our dataset in the format https://github.com/facebookresearch/audiocraft/tree/main/dataset/example
###########################################################################################################
import os
import json
import argparse

from tqdm import tqdm
import numpy as np
import pandas as pd
import ffmpeg

SPLIT_TXTS = "../11. Split dataset/3. split/splits"
VIDEOS_CSV = "../11. Split dataset/2. downsample/videos_info.csv"
GENRES_CSV = "/app/dataset/deepseek_genres.csv"
GENRES = ["Platform", "Sports", "RPG", "Fighting", "Action", "Shooters", "Puzzle", "Strategy", "Racing", "Simulation", "Adventure"]

def get_splits_games() -> dict[str, list[str]]:
    """
        Retuns:
            A dict where the keys are the splits and the values are the list of games that belong to that split
    """
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

def select_n_rand_games_for_splits(split_dict:dict[str, list[str]], n:int=-1, splits:list[str]=['eval', 'test']):
    """
        Selects `n` games for each genre for each of the `splits` according to the `split_dict`

        Args:
            split_dict: A dict returned by the `get_splits_games` function.
            n: number of games to randomly select for each genre inside the splits games. 
                If genre has `less than n games` or `n <= 0`, we get all of its games.
            splits: splits to apply this selection

        Returns:
            Same as `get_splits_games` return
    """
    for split in splits:
        split_games = split_dict[split]
        choosen_games = []

        # Get the genres mapping
        genres_df = pd.read_csv(GENRES_CSV)

        # Draw n games for each genre, 
        for genre in GENRES:
            genres_series = genres_df['game_genre']
            genre_specific_df = genres_df[genres_series == genre]

            genre_specific_games = genre_specific_df['game_folder'].to_numpy()
            genre_specific_games = [game for game in genre_specific_games if game in split_games]

            if n > 0 and len(genre_specific_games) > n:
                genre_specific_games = np.random.choice(genre_specific_games, n, replace=False).tolist()

            choosen_games += genre_specific_games

        split_dict[split] = choosen_games

    return split_dict

def convert_soundtrack_videos(dataset_root:str, split_path:str, soundtrack_df:pd.DataFrame):
    """
        Audiocraft dataset have the format

            my_dataset/split
                |_audio_001.mp3
                |_audio_001.json

        The audio will be the soundtrack.
        The json will acctually be many, one for each of the soundtrack's video. It will contain the
        video description the path to the corresponding soundtrack and the path to the segment's mp4.
        This will minimize the amount of adaptations on the AudioCraft code, including no change in
        how samples are drawn from the dataset.

        We'll use videos_csv to get the selected segments and create links for the soundtracks
        instead of copying the whole audio.
    """
    soundtrack = soundtrack_df['soundtrack'].iloc[0]
    game = soundtrack_df['game_id'].iloc[0]

    # Try to get soundtrack meta
    soundtrack_orig_path = os.path.join(dataset_root, game, 'soundtracks', soundtrack+'.mp3')

    try:
        probe:dict = ffmpeg.probe(soundtrack_orig_path)
    except Exception as e:
        print(f"Erro in ffmpeg.prob for game {game} in {soundtrack}")
        return
        # the soundtracks that failed probe simply do not exist:
        # lufia-ii-rise-of-the-sinistrals-[lufia]-1994 in soundtrack_0059
        # lufia-ii-rise-of-the-sinistrals-[lufia]-1994 in soundtrack_0060
        # lufia-ii-rise-of-the-sinistrals-[lufia]-1994 in soundtrack_0062

        # Clearly this is a problem with mapping, because in the game names
        # lufia-ii-rise-of-the-sinistrals-[lufia]
        # lufia-ii-rise-of-the-sinistrals-[lufia]-1994
        # After the dejavu step the both would be changed to 
        # lufia-ii-rise-of-the-sinistrals
        # because there is a .split("[")[0] in mapping.py and drop_database.py
        # TODO: This games were removed from the dataset, might be a good thing to come back and fix them

    # Create link for the soundtrack in the converted dataset
    soundtrack_tgt_file = f"{game}_{soundtrack}.mp3"
    soundtrack_tgt_path= os.path.join(split_path, soundtrack_tgt_file)

    if not os.path.exists(soundtrack_tgt_path):
        os.symlink(soundtrack_orig_path, soundtrack_tgt_path)

    # Loop soundtrack videos to create a json into audiocraft/dataset
    for idx, row in enumerate(soundtrack_df.iterrows()):
        _, row = row
        soundtrack, segment = row['soundtrack'], row['segment']
        soundtrack_json_path = soundtrack_tgt_path[:-4]+ '_json_{0:04d}'.format(idx) +'.json'

        if os.path.exists(soundtrack_json_path):
            continue

        # Oringinal paths
        segment_orig_path = os.path.join(dataset_root, game, 'videos', soundtrack, segment)
        description_orig_path = os.path.join(dataset_root, game, 'videos_descriptions', segment[:-3]+'txt')

        # Read description
        with open(description_orig_path, 'r') as f:
            description = f.read().rstrip("\n")

        soundtrack_json = {
            "key": "", 
            "artist": '', #probe['format'].get('tags', {}).get('artist', ''),
            "sample_rate": int(probe['streams'][0]['sample_rate']),
            "file_extension": probe['streams'][0]['codec_name'], 
            "description": description,
            "keywords": "",
            "duration": float(probe['streams'][0]['duration']),
            "bpm": "",
            "genre": "", 
            "title": '', #probe['format'].get('tags', {}).get('title', ''),
            "name": soundtrack_tgt_file, 
            "instrument": "",
            "moods": [],
            # New tags that are not part of the MusicGen examples
            "year": '', #probe['format'].get('tags', {}).get('copyright', ''),
            "video": segment_orig_path,
            "json_idx": idx
        }
        # TODO check on the paper how this keys of the dictionary are used

        with open(soundtrack_json_path, 'w') as f:
            json.dump(soundtrack_json, f, indent=4)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='1. dataset_structure.py')
    parser.add_argument('--original_dataset', type=str, default="/app/dataset/nintendo-snes-spc", help="path for the snes mvdb dataset games folder")
    parser.add_argument('--converted_dataset', type=str, default="/app/code/dataset", help="path to audiocraft/dataset where the converted dataset will be")
    parser.add_argument('--selection_splits', type=str, default="eval, test", help="splits (train, eval, test) to apply selecion of games_per_genre and examples_per_genre")
    parser.add_argument('--games_per_genre', type=int, default=-1, help="number of games to randomly select for each genre for selection_splits splits")
    parser.add_argument('--examples_per_sdtk', type=int, default=1, help="number of exmaples for each soundtrack of each game selected according to games_per_genre")

    args = parser.parse_args()
    original_dataset:str = args.original_dataset
    converted_dataset:str = os.path.join(args.converted_dataset, 'snes_mvdb')
    print(f"original_dataset: {original_dataset}")
    print(f"converted_dataset: {converted_dataset}")

    selection_splits:list[str] = args.selection_splits.split(',')
    selection_splits = [split.strip() for split in selection_splits]
    games_per_genre:int = args.games_per_genre
    examples_per_sdtk:int = args.examples_per_sdtk
    print(f"selection_splits: {selection_splits}, games_per_genre: {games_per_genre}, examples_per_sdtk: {examples_per_sdtk}")

    split_dict = get_splits_games()
    split_dict = select_n_rand_games_for_splits(split_dict=split_dict, n=games_per_genre, splits=selection_splits)

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
            game_df = segments_df[segments_df["game_id"] == game]
            game_soundtracks = game_df["soundtrack"].unique()

            for soundtrack in game_soundtracks:
                soundtrack_df:pd.DataFrame = game_df[game_df['soundtrack'] == soundtrack]
                soundtrack_df.reset_index(inplace=True, drop=True)

                if split in selection_splits:
                    if len(soundtrack_df) > examples_per_sdtk:
                        sampled_indexes = np.random.choice(soundtrack_df.index, examples_per_sdtk)
                        soundtrack_df = soundtrack_df.iloc[sampled_indexes]

                convert_soundtrack_videos(original_dataset, split_path, soundtrack_df)

if __name__ == "__main__":
    main()
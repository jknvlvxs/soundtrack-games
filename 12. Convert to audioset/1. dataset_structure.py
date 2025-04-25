import os
import json

from tqdm import tqdm
import pandas as pd
import ffmpeg

SPLIT_TXTS = "../11. Split dataset/3. split/splits"
VIDEOS_CSV = "../11. Split dataset/2. downsample/videos_info.csv"
DATASET_ROOT = "/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/snes-back/vmdb/nintendo-snes-spc"
CONVERTED_DATASET_PATH = "../12. Convert to audioset/snes_vmdb"

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

def convert_game(split_path:str, game:str, videos_csv:pd.DataFrame):
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
        soundtrack_orig_path = os.path.join(DATASET_ROOT, game, 'soundtracks', soundtrack+'.mp3')

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
            # lufia-ii-rise-of-the-sinistrals-[lufia]-1994
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
            segment_orig_path = os.path.join(DATASET_ROOT, game, 'videos', soundtrack, segment)
            description_orig_path = os.path.join(DATASET_ROOT, game, 'videos_descriptions', segment[:-3]+'txt')

            # Read description
            with open(description_orig_path, 'r') as f:
                description = f.read()

            segments_paths.append(segment_orig_path)
            segments_descriptions.append(description)

        soundtrack_json = {
            "key": "", 
            "artist": probe['format'].get('tags', {}).get('artist', ''),
            "sample_rate": probe['streams'][0]['sample_rate'], #TODO we know they are all 44100, but we might want to get this info to make the code more robust
            "file_extension": probe['streams'][0]['codec_name'], 
            #"description": this field is now replaced by segments_paths/segments_descriptions
            "keywords": "", #TODO should we put some stuff here like chiptune, snes? With all saying the same thing might overfit 
            "duration": probe['streams'][0]['duration'], #TODO ok, we'll need to get the duration anyway 
            "bpm": "", 
            "genre": "", 
            "title": probe['format'].get('tags', {}).get('title', ''), 
            "name": soundtrack_tgt_file, 
            "instrument": "Mix", # TODO should we use mix?
            "moods": [],
            # New tags that are not part of the MusicGen examples
            "year": probe['format'].get('tags', {}).get('copyright', ''),
            "segments_paths": segments_paths,
            "segments_descriptions": segments_descriptions
        }

        with open(soundtrack_json_path, 'w') as f:
            json.dump(soundtrack_json, f, indent=4)

def main():
    split_dict = get_split()
    segments_df = pd.read_csv(VIDEOS_CSV)

    # Create folder where the links will go
    if not os.path.exists(CONVERTED_DATASET_PATH):
        os.mkdir(CONVERTED_DATASET_PATH)

    # Loop the dataset according to the split
    for split, games in split_dict.items():
        split_path = os.path.join(CONVERTED_DATASET_PATH, split)

        if not os.path.exists(split_path):
            os.mkdir(split_path)

        for game in tqdm(games, desc=split):
            convert_game(split_path, game, segments_df)

if __name__ == "__main__":
    main()
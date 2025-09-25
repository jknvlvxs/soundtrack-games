import os
import json
import argparse
import random
from datetime import datetime
import shutil

import pandas as pd
import numpy as np
from tqdm import tqdm

from audiocraft.data.audio import audio_write
from module.decoder.models import gvmgen

def is_mp3(file:str):
    extension = file.split('.')[-1]
    return extension == 'mp3'

def get_genre(genres_df, game):
    genre = genres_df[genres_df['game_folder'] == game]
    genre = genre['game_genre'].to_numpy()
    genre = np.random.choice(genre, 1)[0]

    return genre

def read_dataset_split(dataset_split_path:str, genres_path:str) -> list[dict[str, str]]:
    """
        Returns:
            list of dicts containing relevant information about the samples, like the video path, the audio path and the description
    """
    dataset_split_path = os.path.abspath(dataset_split_path)
    print(f"DATASET SPLIT PATH  {dataset_split_path}")
    samples_dicts:list[dict[str, str]] = []
    genres_df = pd.read_csv(genres_path)

    for file in sorted(os.listdir(dataset_split_path)):
        if is_mp3(file):
            continue

        json_path = os.path.join(dataset_split_path, file)
        json_dict:dict[str, str] = {}
        with open(json_path, 'r') as f:
            general_json_dict = json.load(f)

            json_dict['game'] = general_json_dict['visual_content'].split('/')[-1].split('_')[0]
            json_dict['genre'] = get_genre(genres_df, json_dict['game'])
            json_dict['visual_content'] = general_json_dict['visual_content']
            json_dict['path'] = general_json_dict['path']
            json_dict['description'] = general_json_dict['description']

        samples_dicts.append(json_dict)

    return samples_dicts

def get_one_sample_per_game(samples_dicts:list[dict[str, str]]) -> list[dict[str, str]]:
    # dumb dict in order to process the last game in the samples_dicts list
    #none_dict = {'video': "/app/dataset/nintendo-snes-spc/NONE"}
    #samples_dicts.append(none_dict)

    choosen_samples:list[dict[str, str]] = []

    current_game = ''
    game_dicts = []

    for sample_dict in samples_dicts:
        game = sample_dict['game']

        if current_game == '':
            current_game = game

        if game == current_game:
            game_dicts.append(sample_dict)
        else:
            choosen_sample = random.choice(game_dicts)
            choosen_samples.append(choosen_sample)
            game_dicts.clear()

            current_game = game
            game_dicts.append(sample_dict)

    return choosen_samples

def run_inference(samples_dicts:list[dict[str, str]], state_dict_folder:str, save_path:str, dataset_path:str):
    # Save audios folder structure
    # model_date
    #   |_genre
    #     |_game
    #         |_vid_cp.mp4
    #         |_orig_sdtk.mp3
    #         |_gen_sdtk.wav
    #         |_metadata.json

    inference_path = os.path.join(save_path, 'inference')

    for sample_dict in tqdm(samples_dicts):
        vid_name = sample_dict['visual_content'].split('/')[-1][:-3]
        game_name = sample_dict['visual_content'].split('/')[-1].split('_')[0]
        sdtk_name = '_'.join(sample_dict['path'].split('/')[-1].split('.')[0].split('_')[1:])
        print(f"VIDEO NAME {vid_name} GAME {game_name} SDTK {sdtk_name}")
        vid_dest_folder = os.path.join(inference_path, sample_dict['genre'], sample_dict['game'])

        if not os.path.exists(vid_dest_folder):
            os.makedirs(vid_dest_folder)

        print(f"VID DEST FOLDER {vid_dest_folder}")

        # Video tensor path
        vid_tensor_path = sample_dict['visual_content']

        # Copy video
        vid_dest_path = vid_dest_folder + f'/{vid_name}.mp4'
        if not os.path.exists(vid_dest_path):
            vid_orig_path = os.path.join(dataset_path, game_name, 'videos', sdtk_name, f'{vid_name}.mp4')
            print(f"VID ORIG PATH {vid_orig_path}")
            shutil.copy(vid_orig_path, vid_dest_path)

        # Copy soundtrack
        orig_sdtk = vid_dest_folder + f'/{vid_name}.mp3'
        if not os.path.exists(orig_sdtk):
            shutil.copy(sample_dict['path'], orig_sdtk)

        # Create description txt
        desc_path = vid_dest_folder + f'/{vid_name}.txt'
        desc = sample_dict['description']
        if not os.path.exists(desc_path):
            with open(desc_path, 'w') as f:
                f.write(desc)

        # Generate sountrack
        gen_sdtk = vid_dest_folder + f'/{vid_name}_gen'
        if not os.path.exists(gen_sdtk):
            run_inference_gvmgen(state_dict_folder, vid_tensor_path, gen_sdtk)

def run_inference_gvmgen(state_dict_folder:str, vid_tensor_path, save_path):
    print(f"state_dict_folder {state_dict_folder}")

    model = gvmgen.GVMGen.get_pretrained(state_dict_folder, device='cuda')
    model.set_generation_params(duration=60)

    wave = model.generate([vid_tensor_path])[0]

    audio_write(save_path, wave.cpu(), model.sample_rate, strategy="loudness", loudness_compressor=True)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='test_suite.py')
    parser.add_argument('--state_dict_bin_folder', type=str, default="/app/code/checkpoints", help="path to folder containing state_dict.bin")
    parser.add_argument('--save_path', type=str, default="/app/xps/checkpoints_and_inference", help="path to folder where results will be stored")
    parser.add_argument('--model_name', type=str, default="gvmgen_vanilla", help="model name, also the name of the fodler inside save_path")
    parser.add_argument('--split', type=str, default="test", help="split to be accessed in dataset/snes_mvdb/SPLIT")
    parser.add_argument('--dataset_path', type=str, default="/app/dataset/nintendo-snes-spc", help="path to senes_mvdb games folder. snes_mvdb will be added to access the converted dataset")
    parser.add_argument('--converted_dataset', type=str, default="/app/code/dataset", help="path to audiocraft/dataset. snes_mvdb will be added to access the converted dataset")
    parser.add_argument('--genres_path', type=str, default="/app/dataset/deepseek_genres.csv", help="path to games genres csv")

    args = parser.parse_args()

    state_dict_bin_folder = args.state_dict_bin_folder
    save_path = args.save_path
    model_name = args.model_name
    dataset_path = args.dataset_path
    genres_path = args.genres_path
    dataset_split_path = os.path.join(args.converted_dataset, 'snes_mvdb', args.split)

    date = datetime.now()
    date = date.strftime("%m_%d_%y")
    save_path = os.path.join(args.save_path, f'{model_name}_{date}')

    print(f"model name: {model_name} | model path {state_dict_bin_folder}")
    print(f"dataset_split_path: {dataset_split_path}")
    print(f"test suite will be save at: {save_path}")

    random.seed(42)

    # Read dataset split, select samples and run inference
    samples_dicts = read_dataset_split(dataset_split_path, genres_path)
    samples_dicts = get_one_sample_per_game(samples_dicts)

    # for sample_dict in samples_dicts:
    #     print(sample_dict['game'], sample_dict['audio'], sample_dict['genre'])

    run_inference(samples_dicts, state_dict_bin_folder, save_path, dataset_path)

if __name__ == "__main__":
    main()
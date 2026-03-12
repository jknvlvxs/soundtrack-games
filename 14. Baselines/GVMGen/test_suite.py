import os
import json
import argparse
import random
from datetime import datetime

import pandas as pd
import numpy as np
from tqdm import tqdm

from audiocraft.data.audio import audio_write
from module.decoder.models import gvmgen

import moviepy.editor as mp
from pydub import AudioSegment

def get_genre(genres_df, game):
    genre = genres_df[genres_df['game_folder'] == game]
    genre = genre['game_genre'].to_numpy()
    genre = np.random.choice(genre, 1)[0]

    return genre

def read_dataset_split(dataset_split_path:str, genres_path:str) -> dict[str, dict[str, dict[str, list[dict]]]]:
    """
        Returns:
            list of dicts containing relevant information about the samples, like the video path, the audio path and the description
    """
    dataset_split_path = os.path.abspath(dataset_split_path)
    # samples_dicts structure
    # {
    #     genre_1: {
    #         game_1: {
    #             audio_1: [game_1_audio_1_content_1, game_1_audio_1_content_2...]
    #         }
    #     }
    # }
    samples_dicts:dict[str, dict[str, dict[str, list[dict]]]] = {}
    genres_df = pd.read_csv(genres_path)

    for file in sorted(os.listdir(dataset_split_path)):
        json_path = os.path.join(dataset_split_path, file)
        game_content:dict[str, str] = {}
        with open(json_path, 'r') as f:
            general_json_dict = json.load(f)

            game = general_json_dict['visual_content'].split('/')[-1].split('_')[0]
            audio = general_json_dict['path']
            genre = get_genre(genres_df, game)
            game_content['visual_content'] = general_json_dict['visual_content']

        if not samples_dicts.get(genre):
            samples_dicts[genre] = {}
        if not samples_dicts[genre].get(game):
            samples_dicts[genre][game] = {}
        if not samples_dicts[genre][game].get(audio):
            samples_dicts[genre][game][audio] = []

        samples_dicts[genre][game][audio].append(game_content)

    return samples_dicts

def get_n_samples_per_game(samples_dicts:dict[str, dict[str, dict[str, list[dict]]]], n:int) -> list[dict[str, str]]:
    choosen_samples:list[dict[str, str]] = []

    for genre_name, genre_games in samples_dicts.items():
        for game_name, game_audios in genre_games.items():
            choosen_audios = game_audios

            # Make sure to get at most 3 different soundtracks
            if len(game_audios.keys()) > n:
                choosen_audios = {}
                chosen_audios_keys = random.choices(list(game_audios.keys()), k=n)
                for key in chosen_audios_keys:
                    choosen_audios[key] = game_audios[key]

            for audio_name, audio_content in choosen_audios.items():
                # Get random video for current soundtrack
                choosen_audio_content = random.choice(audio_content)

                choosen_sample = {
                    'game': game_name,
                    'genre': genre_name,
                    'audio': audio_name,
                    'visual_content': choosen_audio_content['visual_content']
                }

                choosen_samples.append(choosen_sample)

    return choosen_samples

def run_inference(samples_dicts:list[dict[str, str]], state_dict_folder:str, save_path:str, gt_base_path:str):
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
        vid_tensor_path = sample_dict['visual_content']
        vid_name = vid_tensor_path.split('/')[-1][:-3]
        vid_folder_path = os.path.join(inference_path, sample_dict['genre'], sample_dict['game'])

        vid_gt_folder_path = os.path.join(gt_base_path, 'inference', sample_dict['genre'], sample_dict['game'])
        vid_path = vid_gt_folder_path + f'/{vid_name}.mp4'

        if not os.path.exists(vid_folder_path):
            os.makedirs(vid_folder_path)

        print('Generating Vid For:', vid_folder_path)

        # Generate sountrack
        gen_sdtk = vid_folder_path + f'/{vid_name}_gen'
        if not os.path.exists(gen_sdtk):
            run_inference_gvmgen(state_dict_folder, vid_tensor_path, gen_sdtk)

        video_mp = mp.VideoFileClip(vid_path)
        audio_clip = AudioSegment.from_wav(gen_sdtk+'.wav')
        audio_clip[0:int(video_mp.duration*1000)].export(gen_sdtk+'.wav')
        # Render generated music into input video
        audio_mp = mp.AudioFileClip(gen_sdtk+'.wav')

        audio_mp = audio_mp.subclip(0, video_mp.duration )
        final = video_mp.set_audio(audio_mp)
        try:
            final.write_videofile(os.path.join(vid_folder_path, vid_name+'_gen.mp4'),
                codec='libx264', 
                audio_codec='aac', 
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
        except Exception as e:
            print(f"error：{e}")
        #os.remove(str(idx)+'.wav')

def run_inference_gvmgen(state_dict_folder:str, vid_tensor_path, save_path):
    print(f"state_dict_folder {state_dict_folder}")

    model = gvmgen.GVMGen.get_pretrained(state_dict_folder, device='cuda')
    model.set_generation_params(duration=11)

    wave = model.generate([vid_tensor_path])[0]

    audio_write(save_path, wave.cpu(), model.sample_rate, strategy="loudness", loudness_compressor=True)

def get_samples_from_df(df_path:str, videos_tensor:str) -> list[dict[str, str]]:
    choosen_samples:list[dict[str, str]] = []

    test_suite_vids = pd.read_csv(df_path)
    for row in test_suite_vids.itertuples(index=False, name=None):
        idx, game, genre, video, audio, description = row

        vid_name = video.split('/')[-1][:-4]
        visual_content = os.path.join(videos_tensor, vid_name+'.pt')

        choosen_sample = {
            'game': game,
            'genre': genre,
            'visual_content': visual_content
        }

        choosen_samples.append(choosen_sample)
    
    return choosen_samples

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='test_suite.py')
    parser.add_argument('--save_path', type=str, default="/home/es119256/dados/xps/checkpoints_and_inference_final", help="path to folder where results will be stored")
    #parser.add_argument('--genres_path', type=str, default="/app/dataset/deepseek_genres.csv", help="path to games genres csv")
    parser.add_argument('--df_path', type=str, default="/home/es119256/dados/xps/checkpoints_and_inference_final/test_suite_videos.csv_02_21_26", help="path to games genres csv")
    parser.add_argument('--split', type=str, default="test", help="split to be accessed in dataset/snes_mvdb/SPLIT")
    parser.add_argument('--converted_dataset', type=str, default="/home/es119256/dados/repos/vmdb/14. Baselines/GVMGen/dataset", help="path to audiocraft/dataset. snes_mvdb will be added to access the converted dataset")
    parser.add_argument('--videos_tensor', type=str, default="/home/es119256/dados/datasets/vmdb_3/videos_tensors", help="path to audiocraft/dataset. snes_mvdb will be added to access the converted dataset")
    parser.add_argument('--state_dict_bin_folder', type=str, help="path to folder containing state_dict.bin")
    parser.add_argument('--model_name', type=str, default="GVMGen_Tuned", help="model name, also the name of the fodler inside save_path")

    args = parser.parse_args()

    state_dict_bin_folder = args.state_dict_bin_folder
    save_path = args.save_path
    gt_base_path = os.path.join(save_path, 'Ground_Truth')
    model_name = args.model_name
    # genres_path = args.genres_path
    dataset_split_path = os.path.join(args.converted_dataset, 'snes_mvdb', args.split)

    date = datetime.now()
    date = date.strftime("%m_%d_%y")
    save_path = os.path.join(args.save_path, f'{model_name}_{date}')

    print(f"model name: {model_name} | model path {state_dict_bin_folder}")
    print(f"dataset_split_path: {dataset_split_path}")
    print(f"test suite will be save at: {save_path}")

    random.seed(42)

    # Read dataset split, select samples and run inference
    # samples_dicts = read_dataset_split(dataset_split_path, genres_path)
    # samples_dicts = get_n_samples_per_game(samples_dicts, 3)
    samples_dicts = get_samples_from_df(args.df_path, args.videos_tensor)

    # Debug
    # game = ''
    # n_games = 0
    # n_samples = 0
    # for sample_dict in samples_dicts:
    #     append = ''
    #     if sample_dict['game'] != game: 
    #         game = sample_dict['game']
    #         n_games += 1
    #         append = '\n'

    #     print(append, sample_dict['game'], sample_dict['genre'])
    #     n_samples += 1

    # print(f"\nN Games: {n_games} | N Samples {n_samples}")

    run_inference(samples_dicts, state_dict_bin_folder, save_path, gt_base_path)

if __name__ == "__main__":
    main()
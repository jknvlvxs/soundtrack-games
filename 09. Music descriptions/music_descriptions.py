import os
import argparse
import traceback
import logging
import json
import atexit
import time
from concurrent.futures import ProcessPoolExecutor
import requests

from tqdm import tqdm

import torch
from ollama_deepseek_api import OllamaChat

SEED = 42
session: requests.Session

class Config():
    def __init__(self, prompt:str, video_desc_path:str, music_desc_path:str) -> None:
        self.prompt=prompt
        self.video_desc_path=video_desc_path
        self.music_desc_path=music_desc_path

SINGLE_GENRE = Config(
    prompt="You will receive a description of a gameplay video. The video description starts by differentiating between static (menu, inventory, and map) scenes and gameplay ones. If it is a gameplay, it will also describe the actions happening, the environment, the movement speed, and the game mechanics. In both cases, it will describe the art style and the possible game genre. Your task will be to respond with a music description that fits such a video. Your response will be sent into a text-to-music model that expects a music description like in the following example: 'A grand orchestral arrangement with thunderous percussion, epic brass fanfares, and soaring strings, creating a cinematic atmosphere fit for a heroic battle'. You must put your response between answer tags, like <answer>MUSIC_DESCRIPTION</answer>, where MUSIC_DESCRIPTION is the text of your answer describing the song.",
    video_desc_path="videos_descriptions",
    music_desc_path="music_descriptions"
)

MULTI_GENRE = Config(
    prompt="You will receive a description of a gameplay video. The video description starts by differentiating between static (menu, inventory, and map) scenes and gameplay ones. If it is a gameplay, it will also describe the actions happening, the environment, the movement speed, and the game mechanics. In both cases, it will describe the art style and the possible game genres. Your task will be to respond with a music description that fits such a video. Your response will be sent into a text-to-music model that expects a music description like in the following example: 'A grand orchestral arrangement with thunderous percussion, epic brass fanfares, and soaring strings, creating a cinematic atmosphere fit for a heroic battle'. You must put your response between answer tags, like <answer>MUSIC_DESCRIPTION</answer>, where MUSIC_DESCRIPTION is the text of your answer describing the song.",
    video_desc_path="videos_descriptions_mg",
    music_desc_path="music_descriptions_mg"
)

CONFIG = MULTI_GENRE

def get_descriptions_paths(dataset_folder):
    g_loger = logging.getLogger('global_logger')

    files = []
    skiped = 0
    for game_folder in sorted(os.listdir(dataset_folder)):
        videos_descriptions_folder = os.path.join(dataset_folder, game_folder, CONFIG.video_desc_path)
        music_descriptions_folder = os.path.join(dataset_folder, game_folder, CONFIG.music_desc_path)

        if os.path.exists(videos_descriptions_folder):
            for video_description_file in sorted(os.listdir(videos_descriptions_folder)):
                video_description_file_path = os.path.join(videos_descriptions_folder, video_description_file)
                music_description_file_path = os.path.join(music_descriptions_folder, video_description_file[:-3]+'json')

                if not os.path.exists(music_description_file_path):
                    files.append((video_description_file_path, music_description_file_path))
                else:
                    print(f"SKIPING {video_description_file_path}")
                    skiped += 1

    g_loger.warning(f"SKIPED {skiped}")

    return files

def init_process():
    global session
    session = requests.Session()
    atexit.register(session.close)

def get_video_description_from_file(file:str) -> str:
    with open(file) as f:
        return f.read()

def format_deepseek_res(res:str) -> dict[str, str]:
    # Get think
    think = res.split('<think>\n')
    think = think[0] if len(think) == 1 else think[1]
    think = think.split('\n</think>')[0]

    # Get answer
    music_prompt = res.split('\n</think>')
    music_prompt = music_prompt[0] if len(music_prompt) == 1 else music_prompt[1]
    music_prompt = music_prompt.split('<answer>')[1]
    music_prompt = music_prompt.split('</answer>')[0]

    return {
        'think': think,
        'music_prompt': music_prompt
    }

def run_ollama(pid:int, videos_paths:list[tuple[str, str]]) -> dict[str, bool|int]:
    """
        Run inference in DeepSeek R1 on a set of videos descriptions, to get a music description

        Args:
            video_process: a tuple containing a int to identify the process and a list of tuples with the video description path and the music description path

        Will create a folder called music_descriptions in the videos parent dir containing the descricriptions in txt files with the same name
        as the videos descriptions files
    """
    g_loger = logging.getLogger('global_logger')

    g_loger.warning(f"Process {pid} with {len(videos_paths)} videos, from {videos_paths[0][0].split('/')[-1]} to {videos_paths[-1][0].split('/')[-1]}")

    video_description_path = ""
    current_idx = 0
    try:
        chat = OllamaChat(SEED, 1)
        res = chat.send(
                CONFIG.prompt,
                setup=True
            )

        for current_idx, descriptions_paths in tqdm(enumerate(videos_paths), total=len(videos_paths), desc=f'Process {pid}'):
            video_description_path, music_description_path = descriptions_paths

            music_descriptions_folder = os.path.abspath(os.path.join(music_description_path, os.path.pardir))

            if not os.path.isdir(music_descriptions_folder):
                os.mkdir(music_descriptions_folder)

            # Get video description and generated music description
            video_description = get_video_description_from_file(video_description_path)

            res = chat.send(video_description)
            music_description_dict = format_deepseek_res(res)

            with open(music_description_path, "w") as json_file: 
                json.dump(music_description_dict, json_file, indent=4)

            g_loger.warning(video_description_path.split('/')[-1] + ': ' + music_description_dict['music_prompt'])

    except Exception as e:
        g_loger.critical(f"Error in process {pid} for video at idx {current_idx}: {video_description_path}")
        g_loger.critical(traceback.format_exc())

        return {
            'succeeded': False,
            'current_idx': current_idx
        }

    return {
        'succeeded': True,
    }

def save_failed_video_description(descriptions_paths:tuple[str, str], file_path: str):
    video_description_path, music_description_path = descriptions_paths
    with open(file_path, 'a') as jsonl_file:
        json.dump(
            {
                'video_description_path': video_description_path,
                'music_description_path': music_description_path
            },
            jsonl_file
        )
        jsonl_file.write('\n')

def run_ollama_observer(video_process:tuple[int, list[tuple[str, str]]], args):
    """
        This will be a parent process to run_ollama to keep an eye on it
        In case it fails, the process will resume skipping the problematic video description
        Problematic videos will be logged in the --save_failed_path
    """
    pid, videos_paths = video_process

    with ProcessPoolExecutor(initializer=init_process) as executor:
        succeeded = False

        while not succeeded:
            future = executor.submit(run_ollama, pid, videos_paths)
            result = future.result()

            succeeded = result['succeeded']
            if not succeeded:
                current_idx = result['current_idx']
                save_failed_video_description(videos_paths[current_idx], args.save_failed_path)
                videos_paths = videos_paths[current_idx+1:]

if __name__ == '__main__':
    # Logger
    logging.basicConfig(
        level=logging.WARNING,
        format="{name} | {asctime}:{msecs:.0f} | {message}", style="{",
        datefmt="%m/%d %H:%M:%S",
        filename="logs.log",
        filemode='a',
        encoding='utf-8'
    )

    g_loger = logging.getLogger('global_logger')

    # Parse arguments
    parser = argparse.ArgumentParser(description='music_descriptions.py')
    parser.add_argument('--dataset_root', type=str, default="/home/es119256/dados/datasets/vmdb_2/nintendo-snes-spc", help="path for the dataset games folder")
    parser.add_argument('--save_failed_path', type=str, default="/home/es119256/dados/datasets/vmdb_2/task_9_failed_videos.jsonl", help="path for saving the problematic videos")
    parser.add_argument('--n_processes', type=int, default=30, help="number of processes to run in parallel setted in OLLAMA_MAX_LOADED_MODELS inside the Ollama container") 
    args = parser.parse_args()

    # Collect videos descriptions
    videos_paths = get_descriptions_paths(args.dataset_root) # list of tuples with the video description path and the music description path
    n_videos = len(videos_paths)

    g_loger.warning(f"NVIDEOS {n_videos}")

    lin_div = torch.linspace(0, n_videos, args.n_processes+1, dtype=int).tolist() # type: ignore

    videos_process_list:list[tuple[int, list[tuple[str, str]]]] = [] # list to wrap a list of videos per process

    # Split games across processes
    for idx in range(len(lin_div)-1):
        videos_process_list.append(
            (idx, videos_paths[lin_div[idx]:lin_div[idx+1]])
        )

    g_start_time = time.perf_counter()

    # Create processes
    with ProcessPoolExecutor(initializer=init_process) as executor:
        futures = [executor.submit(run_ollama_observer, video_process, args) for video_process in videos_process_list]

    g_elapsed_time = time.perf_counter() - g_start_time

    g_loger.warning(f"\n\nIt took: {g_elapsed_time}")
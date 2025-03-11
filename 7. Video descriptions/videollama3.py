import os
import argparse
import traceback
import logging

import atexit
import time
from concurrent.futures import ProcessPoolExecutor
import requests

from tqdm import tqdm

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoProcessor

SEED = 42
# Start from cuda:0 and occupy the ones that follow it
DEVICE_START = 0
# One model running takes something like 20GB of VRAM. One A100 can take like 4 in parallel but it is safer to use 3
PROCESSES_PER_GPU = 3
# Generate descriptions every STRIDE videos, e.g. if 10 it will take videos 0,10,20,30... which is equivalent to a stride of 9.
# This is because adjacent videos will have similar descriptions.
GEN_EVERY = 10
MODEL_PATH = "DAMO-NLP-SG/VideoLLaMA3-7B"

session: requests.Session

def init_process():
    global session
    session = requests.Session()
    atexit.register(session.close)

def run_videollama(video_process:tuple[int, str, list[str]]):
    """
        Run inference in VideoLlama on a set of videos

        Args:
            video_process: a tuple containing a int to identify the process, a string with the device like "cuda:0", a list of paths to the videos

        Will create a folder called videos_descriptions in the videos parent dir containing the descricriptions in txt files with the same name
        as the videos files
    """
    transformers.set_seed(SEED) # Always reset the seed to make every single example more easily reproducible

    g_loger = logging.getLogger('global_logger')

    pid, gpu, videos_paths = video_process
    g_loger.warning(f"Process {pid} running on GPU {gpu} with {len(videos_paths)} videos, from from {videos_paths[0].split("/")[-1]} to {videos_paths[-1].split("/")[-1]}")

    try:
        # Model
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
            device_map=gpu,
            torch_dtype=torch.bfloat16,
            attn_implementation="flash_attention_2",
        )

        for video_path in tqdm(videos_paths, desc=f'Process {pid}'):
            game_folder = os.path.abspath(os.path.join(video_path, os.pardir, os.pardir))

            videos_descriptions_folder = os.path.join(game_folder, 'videos_descriptions')

            video_file_name = video_path.split('/')[-1]
            result_txt_path = os.path.join(videos_descriptions_folder, video_file_name[:-3]+"txt")

            if not os.path.isdir(videos_descriptions_folder):
                os.mkdir(videos_descriptions_folder)

            # Video Logger
            vid_logger = logging.getLogger(video_file_name)
            vid_log_f = logging.FileHandler(result_txt_path, 'a', 'utf-8')
            vid_logger.addHandler(vid_log_f)

            conversation = [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": [
                        {"type": "video", "video": {"video_path":video_path, "fps": 5}},
                        {"type": "text", "text": "What is the type of scene in this gameplay video?"},
                        {"type": "text", "text": "If it is a menu, a map, or other kind of static scene, describe the possible options, text and background."},
                        {"type": "text", "text": "If it is a gameplay, describe the actions happening, the environment, the movement speed and the game mechanics."},
                        {"type": "text", "text": "Describe the game art style and genre."}
                    ]
                }
            ]

            processor = AutoProcessor.from_pretrained(MODEL_PATH, trust_remote_code=True)

            inputs = processor(
                conversation=conversation,
                add_system_prompt=True,
                add_generation_prompt=True,
                return_tensors="pt"
            )

            inputs = {k: v.to(gpu) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}

            if "pixel_values" in inputs:
                inputs["pixel_values"] = inputs["pixel_values"].to(torch.bfloat16)

            output_ids = model.generate(**inputs, max_new_tokens=512, top_k=20)
            response = processor.batch_decode(output_ids, skip_special_tokens=True)[0].strip()

            vid_logger.warning(response)

            del processor
            del inputs
            del output_ids
            del response

    except Exception as e:
        g_loger.critical(traceback.format_exc())

def get_videos_paths(dataset_folder):
    files = []
    skiped = 0 
    for game_folder in sorted(os.listdir(dataset_folder)):
        videos_folder = os.path.join(dataset_folder, game_folder, 'videos')
        videos_descriptions_folder = os.path.join(dataset_folder, game_folder, 'videos_descriptions')

        count = 0
        for video_file in sorted(os.listdir(videos_folder)):
            video_path = os.path.join(videos_folder, video_file)
            result_txt_path = os.path.join(videos_descriptions_folder, video_file[:-3]+"txt")

            if count % GEN_EVERY == 0:
                if os.path.exists(result_txt_path):
                    print(f"Skiped {video_file}")
                    skiped+=1
                else:
                    files.append(video_path)

            count+=1

    print(f"SKIPED {skiped}")
    return files

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
    parser = argparse.ArgumentParser(description='videollama3.py')
    # "../5. Database/nintendo-snes-spc/"
    parser.add_argument('--dataset_root', type=str, default="/app/dataset/nintendo-snes-spc", help="path for the dataset games folder")
    parser.add_argument('--n_processes', type=int, default=9, help="number of processes to run in parallel") 
    args = parser.parse_args()

    # Collect videos
    videos_paths = get_videos_paths(args.dataset_root)
    n_videos = len(videos_paths)

    print("NVIDEOS", n_videos)

    lin_div = torch.linspace(0, n_videos, args.n_processes+1, dtype=int).tolist()

    videos_process_list = [] # list to wrap a list of videos per process

    # Split games across processes
    gpu = DEVICE_START
    for idx in range(len(lin_div)-1):
        videos_process_list.append(
            (idx, f'cuda:{gpu}', videos_paths[lin_div[idx]:lin_div[idx+1]])
        )

        if (idx+1) % PROCESSES_PER_GPU == 0:
            gpu += 1

    g_start_time = time.perf_counter()

    # Create processes
    with ProcessPoolExecutor(initializer=init_process) as executor:
        executor.map(run_videollama, videos_process_list)

    g_elapsed_time = time.perf_counter() - g_start_time

    g_loger.warning(f"\n\nIt took: {g_elapsed_time}")
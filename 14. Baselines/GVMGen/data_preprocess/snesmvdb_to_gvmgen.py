import os
import json
import argparse
import atexit
import time
from concurrent.futures import ProcessPoolExecutor
import requests

from tqdm import tqdm
import torch

from utils.video import capture_video

FPS = 3
V_DURATION = 30

def init_process():
    global session
    session = requests.Session()
    atexit.register(session.close)

def is_mp3(file:str):
    extension = file.split('.')[-1]
    return extension == 'mp3'

def save_video_tensor(video_file:str, v_tensor_split:str) -> str:
    name = video_file.split('/')[-1].split('.')[0]
    video_tensor_path = os.path.join(v_tensor_split, name + ".pt")
    
    if not os.path.exists(video_tensor_path):
        video = capture_video(video_file, FPS, 'cuda', V_DURATION)
        torch.save(video, video_tensor_path)
    
    return video_tensor_path

def convert_to_gvmgen(file_path:str, snes_split:str, gvmgen_split:str, v_tensor_split:str) -> tuple[str, dict]:
    #tqdm.write(f"convert_to_gvmgen:\nfile_path:{file_path}\nsnes_split: {snes_split}\ngvmgen_split:{gvmgen_split}\v_tensor_split:{v_tensor_split}")

    with open(file_path, 'r') as f:
        file_dict = json.load(f)

    mp3_name = file_dict['name']
    mp3_path = os.path.join(snes_split, mp3_name)
    video_path = file_dict['video']
    video_tensor_path = save_video_tensor(video_path, v_tensor_split)

    entry = {
        "key": "",
        "artist": "",
        "sample_rate": file_dict['sample_rate'],
        "file_extension": "mp3",
        "visual_content": video_tensor_path,
        "description": "",
        "keywords": "",
        "duration": file_dict['duration'],
        "bpm": "",
        "genre": "",
        "title": "",
        "name": "",
        "instrument": "",
        "moods": "",
        "path": mp3_path,
    }

    file_name = file_path.split('/')[-1]
    json_path = os.path.join(gvmgen_split, file_name)
    with open(json_path, "w") as file:
        file.write(json.dumps(entry, indent=4))

    return (json_path, entry)

def gen_jsonl(json_entries:tuple[str, dict], jsonl_folder:str):
    file_path = os.path.join(jsonl_folder,"data.jsonl")

    with open(file_path, "a") as file:
        json_path, json_entry = json_entries
        video_tensor_path = json_entry['visual_content']
        if os.path.exists(video_tensor_path):
            entry = {
                "path": json_entry['path'],
                "json_path": json_path,
                "duration": json_entry['duration'],
                "sample_rate": json_entry['sample_rate'],
                "amplitude": None,
                "weight": None,
                "info_path": None,
            }

            file.write(json.dumps(entry) + '\n')
        else:
            raise ValueError(f"No label file for {video_tensor_path}")

def covnert_and_generate_json(process: tuple[int, list[dict[str, str]]]):
    pid, jsons_data = process
    tqdm.write(f"Process {pid} received {len(jsons_data)} files")

    for json_data in tqdm(jsons_data, desc=f"PID {pid}"):
        entry = convert_to_gvmgen(
            json_data['json_path'], 
            json_data['snes_mvdb_split_folder'], 
            json_data['gvmgen_split_folder'],
            json_data['video_tensors_split_folder']
        )
        gen_jsonl(entry, json_data['gvmgen_jsonl_split_folder'])

def collect_jsons(splits, snes_mvdb_folder, gvmgen_folder, gvmgen_jsonl_folder, video_tensors_folder) -> list[dict[str, str]]:
    jsons_data = []

    # Loops splits folders
    for split in sorted(os.listdir(snes_mvdb_folder)):
        if split not in splits:
            continue

        snes_mvdb_split_folder = os.path.join(snes_mvdb_folder, split)
        gvmgen_split_folder = os.path.join(gvmgen_folder, split)
        gvmgen_jsonl_split_folder = os.path.join(gvmgen_jsonl_folder, split)
        video_tensors_split_folder = os.path.join(video_tensors_folder, split)

        split_folders = [gvmgen_split_folder, gvmgen_jsonl_split_folder, video_tensors_split_folder]
        for split_folder in split_folders:
            if not os.path.exists(split_folder):
                os.makedirs(split_folder)

        split_files = os.listdir(snes_mvdb_split_folder)[:10]
        tqdm.write(f"SPLIT {split} WILL GET {len(split_files)} FILES")
        for file in sorted(split_files):
            if is_mp3(file):
                continue

            file_path = os.path.join(snes_mvdb_split_folder, file)

            with open(file_path, 'r') as f:
                file_dict = json.load(f)
            video_name = file_dict['video']
            video_name = video_name.split('/')[-1].split('.')[0]
            video_tensor_path = os.path.join(video_tensors_split_folder, video_name + ".pt")

            if os.path.exists(video_tensor_path):
                tqdm.write(f"SKIPPING {split}: {file}")
                continue

            jsons_data.append(
                {
                    'json_path': file_path,
                    'snes_mvdb_split_folder': snes_mvdb_split_folder,
                    'gvmgen_split_folder': gvmgen_split_folder,
                    'gvmgen_jsonl_split_folder': gvmgen_jsonl_split_folder,
                    'video_tensors_split_folder': video_tensors_split_folder
                }
            )

    return jsons_data

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='snesmvdb_to_gvmgen.py')
    parser.add_argument('--snes_mvdb_folder', type=str, default="/app/xps/musicgen_snes_mvdb", help="path to the equivalent of audiocraft/dataset/snes_mvdb")
    parser.add_argument('--splits', type=str, default="train,eval,test", help="splits from snes_mvdb_path split by comma")
    parser.add_argument('--gvmgen_folder', type=str, default="/app/code/dataset/snes_mvdb", help="path to where the converted dataset should go")
    parser.add_argument('--gvmgen_jsonl_folder', type=str, default="/app/code/dataset/snes_mvdb_jsonl", help="path to where the dataset jsonl should go")
    parser.add_argument('--video_tensors_folder', type=str, default="/app/dataset/videos_tensors", help="path to where the videos tensors will be saved")
    parser.add_argument('--n_processes', type=int, default=5, help="number of processes to run in parallel") 

    args = parser.parse_args()
    snes_mvdb_folder = args.snes_mvdb_folder
    splits = args.splits.split(',')
    gvmgen_folder = args.gvmgen_folder
    gvmgen_jsonl_folder = args.gvmgen_jsonl_folder
    video_tensors_folder = args.video_tensors_folder

    jsons_data = collect_jsons(splits, snes_mvdb_folder, gvmgen_folder, gvmgen_jsonl_folder, video_tensors_folder)
    n_jsons = len(jsons_data)
    print(f"N JSONS: {n_jsons}")

    # Split jsons across processes
    lin_div = torch.linspace(0, n_jsons, args.n_processes+1, dtype=int).tolist() # type: ignore

    jsons_process_list = [] # list to wrap a list of videos per process
    for idx in range(len(lin_div)-1):
        jsons_process_list.append(
            (idx, jsons_data[lin_div[idx]:lin_div[idx+1]])
        )

    # Create processes
    g_start_time = time.perf_counter()

    with ProcessPoolExecutor(initializer=init_process) as executor:
        executor.map(covnert_and_generate_json, jsons_process_list)

    g_elapsed_time = time.perf_counter() - g_start_time

    print(f"\n\nIt took: {g_elapsed_time}")

if __name__ == "__main__":
    main()
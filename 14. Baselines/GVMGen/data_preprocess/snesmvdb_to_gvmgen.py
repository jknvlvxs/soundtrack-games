import os
import json
import argparse
from tqdm import tqdm

import torch

from utils.video import capture_video

FPS = 3
V_DURATION = 30

def is_mp3(file:str):
    extension = file.split('.')[-1]
    return extension == 'mp3'

def save_video_tensor(video_file:str, v_tensor_split:str) -> str:
    name = video_file.split('/')[-1].split('.')[0]
    video_tensor_path = os.path.join(v_tensor_split, name + ".pt")
    
    if not os.path.exists(video_tensor_path):
        video = capture_video(video_file, FPS, 'cuda', V_DURATION)
        torch.save(video, video_tensor_path)

        #tqdm.write(f"{video_tensor_path} saved w/ shape {video.shape}\n")
    
    return video_tensor_path

def convert_to_gvmgen(snes_split:str, gvmgen_split:str, v_tensor_split:str) -> list[tuple[str, dict]]:
    entries = []

    split_name = snes_split.split('/')[-1]
    for file in tqdm(sorted(os.listdir(snes_split))[:10], desc=split_name):
        if is_mp3(file):
            continue

        file_path = os.path.join(snes_split, file)

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

        #tqdm.write(str(entry))

        file_name = file_path.split('/')[-1]
        json_path = os.path.join(gvmgen_split, file_name)
        with open(json_path, "w") as file:
           file.write(json.dumps(entry, indent=4))

        entries.append((json_path, entry))

    return entries

def gen_jsonl(json_entries:list[tuple[str, dict]], jsonl_folder:str):
    file_path = os.path.join(jsonl_folder,"data.jsonl")

    with open(file_path, "w") as file:
        for json_path, json_entry in json_entries:
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

                #tqdm.write(str(entry))
                file.write(json.dumps(entry) + '\n')
            else:
                raise ValueError(f"No label file for {video_tensor_path}")

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='snesmvdb_to_gvmgen.py')
    parser.add_argument('--snes_mvdb_folder', type=str, default="/app/xps/musicgen_snes_mvdb", help="path to the equivalent of audiocraft/dataset/snes_mvdb")
    parser.add_argument('--splits', type=str, default="eval,test", help="splits from snes_mvdb_path split by comma")
    parser.add_argument('--gvmgen_folder', type=str, default="/app/code/dataset/snes_mvdb", help="path to where the converted dataset should go")
    parser.add_argument('--gvmgen_jsonl_folder', type=str, default="/app/code/dataset/snes_mvdb_jsonl", help="path to where the dataset jsonl should go")
    parser.add_argument('--video_tensors_folder', type=str, default="/app/dataset/videos_tensors", help="path to where the videos tensors will be saved")

    args = parser.parse_args()
    snes_mvdb_folder = args.snes_mvdb_folder
    splits = args.splits.split(',')
    gvmgen_folder = args.gvmgen_folder
    gvmgen_jsonl_folder = args.gvmgen_jsonl_folder
    video_tensors_folder = args.video_tensors_folder

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

        entries = convert_to_gvmgen(snes_mvdb_split_folder, gvmgen_split_folder, video_tensors_split_folder)
        gen_jsonl(entries, gvmgen_jsonl_split_folder)

if __name__ == "__main__":
    main()
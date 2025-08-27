import os
import json
import argparse

def is_mp3(file:str):
    extension = file.split('.')[-1]
    return extension == 'mp3'

def check_files(snes_mvdb_folder, gvmgen_folder, video_tensors_folder):
    # Loops splits folders
    for split in sorted(os.listdir(snes_mvdb_folder)):
        snes_mvdb_split_folder = os.path.join(snes_mvdb_folder, split)
        gvmgen_split_folder = os.path.join(gvmgen_folder, split)
        video_tensors_split_folder = os.path.join(video_tensors_folder, split)

        count = 0
        for file in sorted(os.listdir(snes_mvdb_split_folder)):
            if is_mp3(file):
                continue
            
            count += 1

            file_path = os.path.join(snes_mvdb_split_folder, file)

            with open(file_path, 'r') as f:
                file_dict = json.load(f)
            
            # Check if the video tensor exists
            video_name = file_dict['video']
            video_name = video_name.split('/')[-1].split('.')[0]
            video_tensor_path = os.path.join(video_tensors_split_folder, video_name + ".pt")

            if not os.path.exists(video_tensor_path):
                print(f"FILE {file} has no video tensor named {video_name + '.pt'}")
            
            # Check if the json file exists
            json_path = os.path.join(gvmgen_split_folder, file)
            if not os.path.exists(json_path):
                print(f"FILE {file} has no JSON")

        print(f"SPLIT {split} GOT {count} FILES")

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='snesmvdb_to_gvmgen.py')
    parser.add_argument('--snes_mvdb_folder', type=str, default="/app/xps/musicgen_snes_mvdb", help="path to the equivalent of audiocraft/dataset/snes_mvdb")
    parser.add_argument('--gvmgen_folder', type=str, default="/app/code/dataset/snes_mvdb", help="path to where the converted dataset should go")
    parser.add_argument('--gvmgen_jsonl_folder', type=str, default="/app/code/dataset/snes_mvdb_jsonl", help="path to where the dataset jsonl should go")
    parser.add_argument('--video_tensors_folder', type=str, default="/app/dataset/videos_tensors", help="path to where the videos tensors will be saved")

    args = parser.parse_args()
    snes_mvdb_folder = args.snes_mvdb_folder
    gvmgen_folder = args.gvmgen_folder
    gvmgen_jsonl_folder = args.gvmgen_jsonl_folder
    video_tensors_folder = args.video_tensors_folder

    check_files(snes_mvdb_folder, gvmgen_folder, video_tensors_folder)

if __name__ == "__main__":
    main()
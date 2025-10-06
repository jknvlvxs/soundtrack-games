import os
import json
import argparse

from tqdm import tqdm

def get_entries(snes_split:str) -> list[tuple[str, dict]]:
    entries = []

    split_name = snes_split.split('/')[-1]
    for file in tqdm(sorted(os.listdir(snes_split)), desc=split_name):
        file_path = os.path.join(snes_split, file)

        with open(file_path, 'r') as f:
            file_dict = json.load(f)

        entries.append((file_path, file_dict))

    return entries

def gen_jsonl(json_entries:list[tuple[str, dict]], jsonl_folder:str):
    file_path = os.path.join(jsonl_folder, "data.jsonl")

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
    parser.add_argument('--snes_mvdb', type=str, default="/app/code/dataset/snes_mvdb", help="path to the equivalent of audiocraft/dataset/snes_mvdb")
    parser.add_argument('--splits', type=str, default="train,eval,test", help="splits from snes_mvdb_path split by comma")
    parser.add_argument('--snes_mvdb_jsonl_folder', type=str, default="/app/code/dataset/snes_mvdb_jsonl_new", help="path to where the dataset jsonl should go")

    args = parser.parse_args()
    snes_mvdb = args.snes_mvdb
    splits = args.splits.split(',')
    snes_mvdb_jsonl_folder = args.snes_mvdb_jsonl_folder

    # Loops splits folders
    for split in sorted(os.listdir(snes_mvdb)):
        if split not in splits:
            continue

        snes_mvdb_split_folder = os.path.join(snes_mvdb, split)
        snes_mvdb_jsonl_split_folder = os.path.join(snes_mvdb_jsonl_folder, split)

        if not os.path.exists(snes_mvdb_jsonl_split_folder):
            os.makedirs(snes_mvdb_jsonl_split_folder)

        entries = get_entries(snes_mvdb_split_folder)
        gen_jsonl(entries, snes_mvdb_jsonl_split_folder)

if __name__ == "__main__":
    main()
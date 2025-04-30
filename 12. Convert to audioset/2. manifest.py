####################################################################################################################################################################
# To create the jsonl manifest file referencing the dataset's audios as in https://github.com/facebookresearch/audiocraft/blob/main/egs/example/data.jsonl
#
#  Jsonl file with jsons following the format
# example = {
#     "path": "dataset/example/electro_2.mp3",
#     "duration": 20.035918367346937, 
#     "sample_rate": 44100, 
#     "amplitude": None, 
#     "weight": None, 
#     "info_path": None
# }
#
# They should be in the audiocraft/egs/split/example.jsonl
####################################################################################################################################################################

import os
import json
import argparse

def is_mp3(file:str):
    extension = file.split('.')[-1]
    return extension == 'mp3'

def get_manifest_dict(converted_dataset:str, split_path:str) -> list[dict[str, any]]:
    manifest_jsons = []

    for file in sorted(os.listdir(split_path)):
        if is_mp3(file):
            continue

        file_path = os.path.join(split_path, file)

        with open(file_path, 'r') as f:
            file_dict = json.load(f)

        dataset_name = converted_dataset.split('/')[-1]
        mp3_name = file_dict['name']
        mp3_path = f'dataset/{dataset_name}/{mp3_name}'

        manifest_json = {
            "path": mp3_path,
            "duration": file_dict['duration'],
            "sample_rate": file_dict['sample_rate'],
            "amplitude": None,
            "weight": None,
            "info_path": None
        }

        manifest_jsons.append(manifest_json)

    return manifest_jsons

def write_jsonl(manifest_jsons:list[dict[str, any]], manifest_path:str):
    with open(manifest_path, 'a') as f:
        for manifest_json in manifest_jsons:
                json.dump(manifest_json, f)
                f.write('\n')

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='2. manifest.py')
    parser.add_argument('--egs_path', type=str, default="/app/audiocraft/egs", help="path to audiocraft/egs")
    parser.add_argument('--converted_dataset', type=str, default="/app/audiocraft/dataset", help="path to audiocraft/dataset snes_mvdb will be added to access the converted dataset")

    args = parser.parse_args()
    egs_path = os.path.join(args.egs_path, 'snes_mvdb')
    converted_dataset = os.path.join(args.converted_dataset, 'snes_mvdb')

    # Loops splits folders
    for split in sorted(os.listdir(converted_dataset)):
        split_path = os.path.join(converted_dataset, split)
        manifest_folder = os.path.join(egs_path, split)
        manifest_path = os.path.join(manifest_folder, 'data.jsonl')

        if not os.path.exists(manifest_folder):
            os.makedirs(manifest_folder)

        manifest_jsons = get_manifest_dict(converted_dataset, split_path)

        write_jsonl(manifest_jsons, manifest_path)

if __name__ == "__main__":
    main()
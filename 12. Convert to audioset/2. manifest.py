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

from tqdm import tqdm

CONVERTED_DATASET_PATH = "../12. Convert to audioset/audiocraft/dataset/snes_vmdb"
MANIFEST_PATH = "../12. Convert to audioset/audiocraft/egs"

def is_mp3(file:str):
    extension = file.split('.')[-1]
    return extension == 'mp3'

def get_manifest_dict(split_path:str) -> list[dict[str, any]]:
    manifest_jsons = []

    for file in sorted(os.listdir(split_path)):
        if is_mp3(file):
            continue

        file_path = os.path.join(split_path, file)

        with open(file_path, 'r') as f:
            file_dict = json.load(f)

        dataset_name = CONVERTED_DATASET_PATH.split('/')[-1]
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
    # Loops splits folders
    for split in sorted(os.listdir(CONVERTED_DATASET_PATH)):
        split_path = os.path.join(CONVERTED_DATASET_PATH, split)
        manifest_folder = os.path.join(MANIFEST_PATH, split)
        manifest_path = os.path.join(manifest_folder, 'data.jsonl')

        os.mkdir(manifest_folder)

        manifest_jsons = get_manifest_dict(split_path)

        write_jsonl(manifest_jsons, manifest_path)

if __name__ == "__main__":
    main()
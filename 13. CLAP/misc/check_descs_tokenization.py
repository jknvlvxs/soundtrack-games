######################################################################################
# LAION-CLAP, and therefore MusicGen configuration for text-consistency, makes use of 
# Robertas' tokenizer trucating at 77 tokens
# This code aims to get an idea about how this truncation may be affecting our video 
# descriptions, since they're probably much larger than that
######################################################################################
import os
import typing as tp

from transformers import RobertaTokenizer

ROOT_PATH = '/app/dataset/nintendo-snes-spc'

class Config():
    def __init__(self, video_desc_path:str, music_desc_path:str) -> None:
        self.video_desc_path=video_desc_path
        self.music_desc_path=music_desc_path

SINGLE_GENRE = Config(
    video_desc_path="videos_descriptions",
    music_desc_path="music_descriptions"
)

MULTI_GENRE = Config(
    video_desc_path="videos_descriptions_mg",
    music_desc_path="music_descriptions_mg"
)

CONFIG = MULTI_GENRE

class Tokenizer:
    def __init__(self) -> None:
        self.tokenizer:RobertaTokenizer = RobertaTokenizer.from_pretrained('roberta-base')

    def tokenize(self, texts: tp.Union[str, tp.List[str]]):
        # we use the default params from CLAP module here as well
        return self.tokenizer(texts, padding="max_length", truncation=True, max_length=77, return_tensors="pt")

    def decode(self, token_ids):
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

def get_descriptions_paths(dataset_folder):
    files = []

    for game_folder in sorted(os.listdir(dataset_folder)):
        videos_descriptions_folder = os.path.join(dataset_folder, game_folder, CONFIG.video_desc_path)

        if os.path.exists(videos_descriptions_folder):
            for video_description_file in sorted(os.listdir(videos_descriptions_folder)):
                video_description_file_path = os.path.join(videos_descriptions_folder, video_description_file)

                files.append(video_description_file_path)

    return files

def main():
    videos_descs_paths = get_descriptions_paths(ROOT_PATH)
    tokenizer = Tokenizer()

    for desc_path in videos_descs_paths:
        with open(desc_path, 'r') as f:
            desc = f.read()

        tokenized = tokenizer.tokenize(desc)['input_ids'].squeeze(dim=0) # type: ignore
        decoded = tokenizer.decode(tokenized)

        print("Origninal:\n", desc)
        print("Decoded:\n", decoded)
        percentage = round(len(decoded)/len(desc) * 100, 2)
        print(f"\nDecoded is {percentage}% of the original")

        return

if __name__ == "__main__":
    main()
import os
import shutil

class Config():
    def __init__(self, music_desc_path:str) -> None:
        self.music_desc_path=music_desc_path

SINGLE_GENRE = Config(
    music_desc_path="music_descriptions"
)

MULTI_GENRE = Config(
    music_desc_path="music_descriptions_mg"
)

CONFIG = SINGLE_GENRE

#ROOT = '/app/dataset/nintendo-snes-spc'
ROOT = '/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/mock'

for game_folder in sorted(os.listdir(ROOT)):
    music_descriptions_folder = os.path.join(ROOT, game_folder, CONFIG.music_desc_path)

    if os.path.exists(music_descriptions_folder):
        print(music_descriptions_folder)
        shutil.rmtree(music_descriptions_folder)
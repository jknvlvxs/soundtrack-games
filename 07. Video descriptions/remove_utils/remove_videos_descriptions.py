import os
import shutil

ROOT = '/app/dataset/nintendo-snes-spc'

for game_folder in sorted(os.listdir(ROOT)):
    videos_folder = os.path.join(ROOT, game_folder, 'videos')
    videos_descriptions_folder = os.path.join(ROOT, game_folder, 'videos_descriptions')

    if os.path.exists(videos_descriptions_folder):
        shutil.rmtree(videos_descriptions_folder)
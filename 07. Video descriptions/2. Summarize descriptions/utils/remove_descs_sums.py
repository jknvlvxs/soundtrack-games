import os
import shutil

ROOT = '/home/es119256/dados/datasets/mock/nintendo-snes-spc'

for game_folder in sorted(os.listdir(ROOT)):
    videos_folder = os.path.join(ROOT, game_folder, 'videos')
    videos_descriptions_folder = os.path.join(ROOT, game_folder, 'descs_sums_mg')

    if os.path.exists(videos_descriptions_folder):
        shutil.rmtree(videos_descriptions_folder)
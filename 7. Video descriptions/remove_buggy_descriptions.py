# Remove empty descriptions

import os
import shutil

ROOT = '/app/dataset/nintendo-snes-spc'

for game_folder in sorted(os.listdir(ROOT)):
    videos_folder = os.path.join(ROOT, game_folder, 'videos')
    videos_descriptions_folder = os.path.join(ROOT, game_folder, 'videos_descriptions')

    if os.path.exists(videos_descriptions_folder):
        for description_file in sorted(os.listdir(videos_descriptions_folder)):

            description_path = os.path.join(videos_descriptions_folder, description_file)
            with open(description_path, mode='r') as f:
                description_text = f.read()
                if description_text == '':
                    os.remove(description_path)
                    print(description_file)
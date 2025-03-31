# Remove descriptions that are out of the stride
# this is because descriptions were beeing generated while dejavu was running
import os
from videollama3 import get_videos_paths

ROOT = '/app/dataset/nintendo-snes-spc'

files = get_videos_paths(ROOT)

files_descriptions = [file[1] for file in files]

for game_folder in sorted(os.listdir(ROOT)):
    videos_folder = os.path.join(ROOT, game_folder, 'videos')
    videos_descriptions_folder = os.path.join(ROOT, game_folder, 'videos_descriptions')

    if os.path.exists(videos_descriptions_folder):
        descriptions = os.listdir(videos_descriptions_folder)

        for description in descriptions:
            description_path = os.path.join(videos_descriptions_folder, description)
            if description_path not in files_descriptions:
                print(description_path)
                os.remove(description_path)
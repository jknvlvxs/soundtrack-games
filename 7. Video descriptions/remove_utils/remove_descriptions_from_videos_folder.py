# Remove descriptions that wrongly went inside videos folder

import os
import shutil

ROOT = '/app/dataset/nintendo-snes-spc'

for game_folder in sorted(os.listdir(ROOT)):
    videos_folder = os.path.join(ROOT, game_folder, 'videos')

    for video_or_folder in sorted(os.listdir(videos_folder)):
        video_or_folder_path = os.path.join(videos_folder, video_or_folder)

        if video_or_folder == 'videos_descriptions':
            shutil.rmtree(video_or_folder_path)
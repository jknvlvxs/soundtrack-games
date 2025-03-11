import os

ROOT = "/app/dataset/nintendo-snes-spc"

for game_folder in sorted(os.listdir(ROOT)):
    desc_folder = os.path.join(ROOT, game_folder, 'videos_descriptions')

    if not os.path.exists(desc_folder):
        print(game_folder)
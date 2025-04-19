# The genres were saved in json files apread across the games foldes, this is to get them in a single csv

import os
import json 

ROOT = '/home/es119256/datasets/vmdb/nintendo-snes-spc'
SAVE_PATH = '/home/es119256/datasets/vmdb/deepseek_genres.csv'

def main():
    with open(SAVE_PATH, 'a') as csv:
        csv.write("game_folder,game_genre\n")

    for game_folder in sorted(os.listdir(ROOT)):
        genre_json_path = os.path.join(ROOT, game_folder, 'genre.json')

        if not os.path.exists(genre_json_path):
            continue

        genre = ""
        with open(genre_json_path, 'r') as json_file:
            game_genre_json = json.load(json_file)
            genre = game_genre_json['genre']

        with open(SAVE_PATH, 'a') as csv:
            csv.write(f"{game_folder},{genre}\n")

if __name__ == '__main__':
    main()
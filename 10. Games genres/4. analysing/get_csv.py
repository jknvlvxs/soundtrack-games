# The genres were saved in json files apread across the games foldes, this is to get them in a single csv

import os
import json 

ROOT = '/home/es119256/dados/datasets/vmdb_2/nintendo-snes-spc'
SAVE_PATH = '/home/es119256/dados/datasets/vmdb_2/deepseek_multi_genres.csv'

def get_higher_amount_of_genres():
    n = -1
    for game_folder in sorted(os.listdir(ROOT)):
        genre_json_path = os.path.join(ROOT, game_folder, 'multi_genres.json')

        if not os.path.exists(genre_json_path):
            continue

        with open(genre_json_path, 'r') as json_file:
            game_genre_json = json.load(json_file)
            genres = game_genre_json['genres']

            if len(genres) > n:
                n = len(genres)
    return n

def main():
    max_genres = get_higher_amount_of_genres()

    with open(SAVE_PATH, 'a') as csv:
        header = ['game_folder'] + [f"genre_{x}" for x in range(max_genres)]
        header = ','.join(header) + "\n"
        csv.write(header)

    for game_folder in sorted(os.listdir(ROOT)):
        genre_json_path = os.path.join(ROOT, game_folder, 'multi_genres.json')

        if not os.path.exists(genre_json_path):
            continue

        with open(genre_json_path, 'r') as json_file:
            game_genre_json = json.load(json_file)
            genres = game_genre_json['genres']

        with open(SAVE_PATH, 'a') as csv:
            line = [game_folder] + genres
            line = ','.join(line) + "\n"
            csv.write(line)

if __name__ == '__main__':
    main()
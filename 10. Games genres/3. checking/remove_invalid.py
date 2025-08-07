import os
import json 

ROOT = '/home/es119256/dados/datasets/vmdb_2/nintendo-snes-spc'
valid_genres = ["Shooters", "Sports", "Platform", "RPG", "Puzzle", "Action", "Fighting", "Strategy", "Simulation", "Adventure", "Racing"]
def main():
    for game_folder in sorted(os.listdir(ROOT)):
        save_path = os.path.join(ROOT, game_folder, 'multi_genres.json')

        if not os.path.exists(save_path):
            continue

        genre = ""
        with open(save_path, 'r') as json_file:
            game_genre_json = json.load(json_file)
            genres = game_genre_json['genres']

        for genre in genres:
            if genre not in valid_genres:
                print(f"{game_folder}: {genre}, {save_path}\n")
                #os.remove(save_path) #letting it commented because this is kind of dangerous

if __name__ == '__main__':
    main()
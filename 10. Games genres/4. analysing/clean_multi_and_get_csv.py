# The genres were saved in json files apread across the games foldes, this is to get them in a single csv
import os
import json 
from copy import deepcopy

ROOT = '/home/es119256/dados/datasets/vmdb/nintendo-snes-spc'
SAVE_PATH = '/home/es119256/dados/datasets/vmdb/deepseek_multi_genres.csv'

valid_genres = ["Shooters", "Sports", "Platform", "RPG", "Puzzle", "Action", "Fighting", "Strategy", "Simulation", "Adventure", "Racing"]

class Rule():
    def __init__(self, variations, valid) -> None:
        self.variations = variations
        self.valid = valid

    def __call__(self, invalid_genre, genres_dict:dict) -> tuple[dict, bool]:
        if invalid_genre in self.variations: # The rule applies
            index = genres_dict["genres"].index(invalid_genre) # get the position of the invalid genre

            if self.valid in genres_dict["genres"]: # If the valid version is already there, delete the invalid one
                del genres_dict["genres"][index]
                return genres_dict, True

            # Replace invalid version with valid one
            genres_dict["genres"][index] = self.valid
            return genres_dict, True

        return genres_dict, False

class DelRule():
    def __init__(self, variations) -> None:
        self.variations = variations

    def __call__(self, invalid_genre, genres_dict:dict) -> tuple[dict, bool]:
        if invalid_genre in self.variations: # The rule applies
            index = genres_dict["genres"].index(invalid_genre) # get the position of the invalid genre

            del genres_dict["genres"][index]
            return genres_dict, True

        return genres_dict, False

rules = [
    # shooters
    Rule(
        variations = ["Shooter", "Shoot 'em Up"],
        valid="Shooters"
    ),
    # fighting
    Rule(
        variations = ["Beat 'em up", "Beat 'em Up", "Combat", "Boxing video game"],
        valid="Fighting"
    ),
    # platform
    Rule(
        variations = ["Platformer"],
        valid="Platform"
    ),
    # rpg
    Rule(
        variations = ["Tactical RPG", "Turn-Based Tactics"],
        valid="RPG"
    ),
    # strategy
    Rule(
        variations = ["Tactical", "Real-Time Tactics"],
        valid="Strategy"
    ),
    # puzzle
    Rule(
        variations = ["Pinball", "Quiz"],
        valid="Puzzle"
    ),
    # remove arcade
    DelRule(
        variations = ["Vehicular Combat", "Arcade", "Maze", "Stealth", "Educational", "Visual Novel", "Casino", "Card", "Rhythm"]
    )
]

def apply_rules(genres_dict):
    any_applied = False
    genres_dbg = deepcopy(genres_dict["genres"]) # stuff for debuging purposes

    # break Action-Adventure
    invalid_genre = "Action-Adventure"
    valid = ["Action", "Adventure"]
    if invalid_genre in genres_dict["genres"]:
        print(genres_dict["genres"])
        index = genres_dict["genres"].index(invalid_genre)
        genres_dict["genres"] = genres_dict["genres"][:index] + valid + genres_dict["genres"][index+1:]

    # clean repeated genres
    genres_dict["genres"] = list(dict.fromkeys(genres_dict["genres"]))

    genres = deepcopy(genres_dict["genres"]) # it's not a good ideia to loop a list that will be modified

    # apply rules
    for genre in genres:
        if genre not in valid_genres:
            for rule in rules:
                genres_dict, applied_rule = rule(genre, genres_dict)

                if applied_rule:
                    any_applied = True

    if any_applied:
        print(genres_dbg)
        print(genres_dict["genres"])
        print()

    return genres_dict

def debug_clean_multi():
    for game_folder in sorted(os.listdir(ROOT)):
        save_path = os.path.join(ROOT, game_folder, 'multi_genres.json')

        if not os.path.exists(save_path):
            #print(f"Game {game_folder} with no multi_genres.json")
            continue

        genre = ""
        with open(save_path, 'r') as json_file:
            genres_dict = json.load(json_file)

        genres_dict = apply_rules(genres_dict)

        # Check if after applied rules there are no invalid genres
        if len(genres_dict["genres"]) == 0:
                print(f"{game_folder}: HAS NO GENRES\n")

        for genre in genres_dict["genres"]:
            if genre not in valid_genres:
                print(f"{game_folder}: {genre}, {save_path}\n")

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
    #max_genres = get_higher_amount_of_genres()
    max_genres = 3 # limiting the maximum amount of genres to 3

    with open(SAVE_PATH, 'a') as csv:
        header = ['game_folder'] + [f"genre_{x}" for x in range(max_genres)]
        header = ','.join(header) + "\n"
        csv.write(header)

    for game_folder in sorted(os.listdir(ROOT)):
        genre_json_path = os.path.join(ROOT, game_folder, 'multi_genres.json')

        if not os.path.exists(genre_json_path):
            continue

        with open(genre_json_path, 'r') as json_file:
            genres_dict = json.load(json_file)

        genres_dict = apply_rules(genres_dict)
        genres = genres_dict['genres'][:max_genres]

        with open(SAVE_PATH, 'a') as csv:
            line = [game_folder] + genres
            line = ','.join(line) + "\n"
            csv.write(line)

if __name__ == '__main__':
    #debug_clean_multi()
    main()

# Manual changes:
# doukyuusei-2 => Changed "Visual Novel" to "Simulation"
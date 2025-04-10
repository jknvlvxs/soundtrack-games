"""
    Use the data gethered from wikidata and the videos descriptions to ask DeekSeek R1 for the games genres
"""
import os
import json
import torch
from tqdm import tqdm

from ollama_deepseek_api import OllamaChat

SEED = 42
ROOT = '/home/es119256/datasets/vmdb/nintendo-snes-spc'
WIKIDATA_PATH = '/home/es119256/datasets/vmdb/wiki_genres.json'

def get_videos_descriptions(description_folder:str, n_chosen=3)->list[str]:
    descriptions = sorted(os.listdir(description_folder))
    n_descriptions = len(descriptions)-1

    # We'll use n_chosen +2, then eliminate the two in the borders, since they are probably meny screens
    lin_div = torch.linspace(0, n_descriptions, n_chosen+2, dtype=int).tolist()[1:-1]

    descriptions_txts:list[str] = []
    for idx in range(len(lin_div)):
        description_file = descriptions[lin_div[idx]]
        description_path = os.path.join(description_folder, description_file)

        with open(description_path, 'r') as f:
            description_txt = f.read()
            descriptions_txts.append(description_txt)

    return descriptions_txts

def get_deepseek_prompt(game_name, wiki_genres:list[str], descriptions:list[str])->str:
    prompt = f"The game name is {game_name}."

    wiki_genres = ', '.join(wiki_genres)
    prompt += f"The game genres obtained from wikidata are: {wiki_genres}."

    prompt += "The descriptions from gameplay videos of this game are:\n\n"
    for idx, description in enumerate(descriptions):
        prompt += f"Description {idx+1}:\n{description}\n"

    return prompt

def get_deepseek_answer(deep_seek_prompt:str):
    chat = OllamaChat(1234, 1)
    res = chat.send(
            "You will receive a game name, a possible list of genres of this game from wikidata and three descriptions of gameplay videos of that game. Your task will be to, given such information, determine the game genre as one of the following list: Shooters, Sports, Platform, RPG, Puzzle, Action, Fighting, Strategy, Simulation, Adventure, Racing. You must put your answer, that is, the genre chosen from the list, in quotes.",
            setup=True
        )

    res = chat.send(deep_seek_prompt)

    return res

def format_deepseek_answer(answer:str) -> dict[str, str]:
    split = answer.split('<think>\n', maxsplit=1)[1].split('\n</think>')
    think, genre = split

    genre = genre.split('"')[1]

    return {
        'think': think,
        'genre': genre
    }

def main():
    games_genres_json = {}

    with open(WIKIDATA_PATH, 'r') as json_file:
        games_genres_json = json.load(json_file)

    for game_folder in tqdm(sorted(os.listdir(ROOT))):
        game_name = game_folder.replace('-', ' ')
        wiki_genres:list[str] = games_genres_json[game_folder]['genres']
        descriptions_folder = os.path.join(ROOT, game_folder, 'videos_descriptions')
        save_path = os.path.join(ROOT, game_folder, 'genre.json')

        if os.path.exists(save_path):
            print(f'Skipping {game_name}')
            continue

        descriptions = get_videos_descriptions(descriptions_folder)
        deep_seek_prompt = get_deepseek_prompt(game_name, wiki_genres, descriptions)
        deepseek_answer = get_deepseek_answer(deep_seek_prompt)
        formated_answer = format_deepseek_answer(deepseek_answer)

        with open(save_path, 'w') as json_file:
            json.dump(formated_answer, json_file, indent=4)

        print(f'{game_name}: {formated_answer} \n\n')

if __name__ == '__main__':
    main()
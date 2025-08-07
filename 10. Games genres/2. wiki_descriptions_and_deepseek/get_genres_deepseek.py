"""
    Use the data gathered from wikidata and the videos descriptions to ask DeekSeek R1 for the games genres
"""
import os
import re
import json
import torch
from tqdm import tqdm

from ollama_deepseek_api import OllamaChat

SEED = 42
ROOT = '/home/es119256/dados/datasets/vmdb_2/nintendo-snes-spc'
WIKIDATA_PATH = '/home/es119256/dados/datasets/vmdb_2/wiki_genres.json'
N_CHOSEN = 5

class Config():
    def __init__(self, prompt:str, video_desc_path:str, json_name:str) -> None:
        self.prompt=prompt
        self.video_desc_path=video_desc_path
        self.json_name=json_name

SINGLE_GENRE = Config(
    prompt=f"You will receive a game name, a possible list of genres of this game from wikidata and {N_CHOSEN} descriptions of gameplay videos of that game. Your task will be to, given such information, determine the game genre as one of the following list: Shooters, Sports, Platform, RPG, Puzzle, Action, Fighting, Strategy, Simulation, Adventure, Racing. You must put your answer in between a genre tag, like <genre>CHOSEN_GENRE</genre>, where CHOSEN_GENRE is the genre you chose from the list.",
    video_desc_path="videos_descriptions",
    json_name="genre.json"
)

MULTI_GENRE = Config(
    prompt= f"You will receive a game name, a possible list of genres of this game from Wikidata, and {N_CHOSEN} descriptions of gameplay videos of that game. Your task will be to, given such information, determine the game's possible genres according to the following list: Shooters, Sports, Platform, RPG, Puzzle, Action, Fighting, Strategy, Simulation, Adventure, Racing. The genres list must be ordered from the most important to the least important. You must put each genre of your answer in between a genre tag, like: '<genre>CHOSEN_GENRE_1</genre> <genre>CHOSEN_GENRE_2</genre>', where CHOSEN_GENRE_INDEX is one of the genres you chose from the genres list. Another important thing is that if the genre is hyphenated, like Action-Adventure, it should be split into <genre>Action</genre> and <genre>Adventure</genre>. If a genre is mentioned in the descriptions but doesn't seem likely to belong to such game, they must be ignored.",
    video_desc_path="videos_descriptions_mg",
    json_name="multi_genres.json"
)

CONFIG = MULTI_GENRE

def get_videos_descriptions(description_folder:str, n_chosen=N_CHOSEN)->list[str]:
    descriptions = sorted(os.listdir(description_folder))
    n_descriptions = len(descriptions)-1

    # We'll use n_chosen +2, then eliminate the two in the borders, since they are probably menu screens
    lin_div = torch.linspace(0, n_descriptions, n_chosen+2, dtype=int).tolist()[1:-1] # type: ignore

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

    wiki_genres = ', '.join(wiki_genres) # type: ignore
    prompt += f"The game genres obtained from wikidata are: {wiki_genres}."

    prompt += "The descriptions from gameplay videos of this game are:\n\n"
    for idx, description in enumerate(descriptions):
        prompt += f"Description {idx+1}:\n{description}\n"

    return prompt

def get_deepseek_answer(deep_seek_prompt:str):
    chat = OllamaChat(1234, 1)
    res = chat.send(
            CONFIG.prompt,
            setup=True
        )

    res = chat.send(deep_seek_prompt)

    return res

def format_deepseek_answer(answer:str) -> dict:
    split = answer.split('<think>\n', maxsplit=1)[1].split('\n</think>')
    think, genres = split

    pattern = rf"<genre(?:[^>]*)>(.*?)</genre>"
    genres = re.findall(pattern, genres)

    return {
        'think': think,
        'genres': genres
    }

def main():
    games_genres_json = {}

    with open(WIKIDATA_PATH, 'r') as json_file:
        games_genres_json = json.load(json_file)

    for game_folder in tqdm(sorted(os.listdir(ROOT))):
        print(f"\n------> RUNNING FOR GAME {game_folder} <------\n")
        game_name = game_folder.replace('-', ' ')
        wiki_genres:list[str] = games_genres_json[game_folder]['genres']
        descriptions_folder = os.path.join(ROOT, game_folder, CONFIG.video_desc_path)
        save_path = os.path.join(ROOT, game_folder, CONFIG.json_name)

        if not os.path.exists(descriptions_folder) or len(os.listdir(descriptions_folder)) < N_CHOSEN:
            print(f'\nSKIPPING {game_name} for insuficient amount of descriptions\n')
            continue

        if os.path.exists(save_path):
            print(f'\nSKIPPING {game_name} because the file already exists\n')
            continue

        descriptions = get_videos_descriptions(descriptions_folder)
        deep_seek_prompt = get_deepseek_prompt(game_name, wiki_genres, descriptions)
        deepseek_answer = get_deepseek_answer(deep_seek_prompt)
        formated_answer = format_deepseek_answer(deepseek_answer)

        with open(save_path, 'w') as json_file:
            json.dump(formated_answer, json_file, indent=4)

        genre = formated_answer["genres"]
        print(f'{game_name}:\n{deepseek_answer}\n\nExtracted genres:{genre}\n\n')

if __name__ == '__main__':
    main()
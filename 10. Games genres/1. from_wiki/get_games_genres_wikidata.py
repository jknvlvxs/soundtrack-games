import os
import json
from wikidata_api import WikiDataAPI

ROOT = '/home/es119256/datasets/vmdb/nintendo-snes-spc'
SAVE_PATH = '/home/es119256/datasets/vmdb/wiki_genres.json'

def get_genre_from_wiki(game_name: str) -> str|None:
    w_api = WikiDataAPI()
    page_results = w_api.query_pages(game_name)

    # For each of the search results we can retrieve the pages and look if they are from games
    genres_list = []
    depth = 0
    game_entity = ''
    for page_res in page_results:
        if depth >= 5:
            break

        game_entity = page_res['title']
        game_entity_claims = w_api.get_entity_claims(game_entity)

        if game_entity_claims.get('P31') != None: # It is a game
            # Get the genre
            genres = game_entity_claims.get('P136')

            if genres != None:
                print(genres)
                for genre in genres:
                    genre_entity = genre['mainsnak']['datavalue']['value']['id']
                    genre = w_api.get_entity_label(genre_entity)
                    genres_list.append(genre)

        depth += 1
    print(genres_list)
    return genres_list, game_entity

def main():
    games_genres_json = {}

    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, 'r') as json_file:
            games_genres_json = json.load(json_file)

    with open(SAVE_PATH, 'w') as json_file:
        for game_folder in sorted(os.listdir(ROOT)):
            if games_genres_json.get(game_folder) != None:
                print(f'Skipping {game_folder}')
                continue

            print(f'@@@@@@@ GAME {game_folder}:')
            game_name = game_folder.replace('-', ' ')
            genres_list, game_entity = get_genre_from_wiki(game_name)

            games_genres_json[game_folder] = {
                'genres': genres_list,
                'entity': game_entity
            }

            json_file.seek(0)
            json.dump(games_genres_json, json_file, indent=4)
            #print(f'{game_folder}: {genres_list}')
            print()

if __name__ == '__main__':
    main()
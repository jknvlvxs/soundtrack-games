import os
import httpx
from tqdm import tqdm
from bs4 import BeautifulSoup
import time

ROOT = '/home/es119256/datasets/vmdb/nintendo-snes-spc'
SAVE_PATH = '/home/es119256/datasets/vmdb/wiki_genres.csv'
# Google API tutorial: https://www.youtube.com/watch?v=4YhxXRPKI0c
CUSTOM_SEARCH_API = os.environ['CUSTOM_SEARCH_API'] # key for a google cloud project with custom search api enabled
SEARCH_ENGINE_ID = os.environ['SEARCH_ENGINE_ID']
BASE_URL = 'https://www.googleapis.com/customsearch/v1'

def search_for_wiki_page(search_string:str) -> str:
    """ 
        Search for a WikiPepdia page on google and return the page name
    """
    headers = {
        'User-Agent': "SNES-MVDB (felipemarra.com) getting-game-genres-for-reasearch"
    }
    params = {
        'key': CUSTOM_SEARCH_API,
        'cx': SEARCH_ENGINE_ID,
        'q': search_string
    }
    res = httpx.get(BASE_URL, params=params, headers=headers)
    res.raise_for_status()
    res = res.json()
    res = res.get('items', [])
    return res[0]['formattedUrl'].split('/')[-1]

def get_genre_from_wiki(search_string: str) -> str|None:
    page = search_for_wiki_page(search_string)

    headers = {
        'User-Agent': "SNES-MVDB (felipemarra.com) getting-game-genres-for-reasearch"
    }
    url = f"https://en.wikipedia.org/wiki/{page}"

    res = httpx.get(url, headers=headers)
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, 'html.parser')

        infobox_table =  soup.find("table", class_='infobox')
        if infobox_table != None:
            infobox_body = infobox_table.find('tbody')
            rows = infobox_body.find_all('tr')

            for row in rows:
                th = row.find('th')
                if th != None and th.text.startswith('Genre'):
                    genre_col = row.find('td')
                    return genre_col.text, url

    return None, url

def main():
    with open(SAVE_PATH, 'a') as f:
        f.write('game_folder, genre, wiki_url\n')

        for game_folder in tqdm(sorted(os.listdir(ROOT))):
            search_string = game_folder.replace('-', ' ') + ' snes'
            genre, url = get_genre_from_wiki(search_string)
            if genre == None:
                f.write(f'{game_folder}, None, "{url}"\n')
                print(f'{game_folder}, {url}')
            else:
                f.write(f'{game_folder}, "{genre}", "{url}"\n')
                print(f'{game_folder}, {genre}')

if __name__ == '__main__':
    main()
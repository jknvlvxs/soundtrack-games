import os
import requests
import json

class WikiDataAPI:
    def __init__(self):
        self.base_url = 'https://www.wikidata.org/w/api.php'
        self.search_depth = 5

    def query_pages(self, game_name):
        """ Query WikiData pages given a game name """

        headers = {
            'User-Agent': "get-games-genres (felipemarra.com)",
            #'Authorization': self.auth
        }

        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': f'{game_name} video game',
            'format': 'json',
        }

        res = requests.get(self.base_url, headers=headers, params=params)
        res = res.json()
        pages = res['query']['search']

        return pages

    def get_entity_claims(self, entity):
        """ Get a WikiData page given a page id """

        headers = {
            'User-Agent': "get-games-genres (felipemarra.com)",
            #'Authorization': self.auth
        }

        params = {
            'action': 'wbgetentities',
            'ids': entity,
            'props': 'claims',
            'format': 'json',
        }

        res = requests.get(self.base_url, headers=headers, params=params)
        res = res.json()

        return res['entities'][entity]['claims']

    def get_entity_label(self, entity):
        # https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q1888768&props=labels&languages=en&format=json
        """ Get a WikiData page given a page id """

        headers = {
            'User-Agent': "get-games-genres (felipemarra.com)",
            #'Authorization': self.auth
        }

        params = {
            'action': 'wbgetentities',
            'ids': entity,
            'props': 'labels',
            'languages': 'en',
            'format': 'json',
        }

        res = requests.get(self.base_url, headers=headers, params=params)
        res = res.json()

        return res['entities'][entity]['labels']['en']['value']
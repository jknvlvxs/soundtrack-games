################################################################################################
# Plot for the audios in the dataset/snes_mvdb from https://github.com/FelipeMarra/visual-bardo
# Same thing as getting the mapped and downsampled audios from https://github.com/jknvlvxs/vmdb
################################################################################################

import os
import typing as tp

import umap
from tqdm import tqdm

import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

import torch

DATASET_ROOT = "/app/dataset/nintendo-snes-spc"
AUDIOCRAFT_DATASET = "/app/xps/musicgen_snes_mvdb"
DEEP_SEEK_GENRES = "/app/dataset/deepseek_genres.csv"
GENRES = ["Shooters", "Sports", "Platform", "RPG", "Puzzle", "Action", "Fighting", "Strategy", "Simulation", "Adventure", "Racing"]

MARKERS = ['o', '^', "<", ">", "1", 's', "p", '*', "+", 'x', "d"]
CMAP = 'viridis'

NEIGHBORS = 15

cmap = matplotlib.colormaps[CMAP]
normalized_colors = np.linspace(0, 1, len(GENRES))
COLORS = [cmap(val) for val in normalized_colors]

def get_embs_paths() -> dict[str, tp.Any]:
    files_dict = {
        "game_color":  [],
        #"genre_mkr": [],
        "emb": []
    }

    genres_df = pd.read_csv(DEEP_SEEK_GENRES)

    # cmap = matplotlib.colormaps[CMAP]
    # normalized_colors = np.linspace(0, 1, len(games_folders))
    # colors = [cmap(val) for val in normalized_colors]

    for split in os.listdir(AUDIOCRAFT_DATASET):
        split_path = os.path.join(AUDIOCRAFT_DATASET, split)
        for file in os.listdir(split_path):
            if file.endswith('.json'):
                continue

            game_name = file.split('_soundtrack')[0]
            soundtrack = 'soundtrack'+file.split('_soundtrack')[1]
            #print(f"game: {game_name}, soundtrack: {soundtrack}")

            game_genre = genres_df[genres_df['game_folder'] == game_name]['game_genre'].to_list()

            if len(game_genre) == 0:
                continue

            game_genre = game_genre[0]

            if game_genre != "RPG":
                continue

            audios_emb_folder = os.path.join(DATASET_ROOT, game_name, 'soundtracks_clap')
            audios_emb_file_path = os.path.join(audios_emb_folder, soundtrack[:-3]+'pt')

            if not os.path.exists(audios_emb_file_path):
                continue

            # game_idx = games_folders.index(game_folder)
            # files_dict["game_color"].append(colors[game_idx])

            #genre_idx = GENRES.index(game_genre)
            #files_dict["genre_mkr"].append(MARKERS[genre_idx])

            genre_idx = GENRES.index(game_genre)
            files_dict["game_color"].append(COLORS[genre_idx])

            files_dict["emb"].append(audios_emb_file_path)

    return files_dict

def get_embs() -> dict[str, tp.Any]:
    files_dict = get_embs_paths()

    all_embs = None
    for emb_path in tqdm(files_dict["emb"]):
        emb:torch.Tensor = torch.load(emb_path).unsqueeze(0)

        if isinstance(all_embs, torch.Tensor):
            all_embs = torch.cat((all_embs, emb), dim=0)
        else:
            all_embs = emb

    files_dict["emb"] = all_embs

    return files_dict

def maerker_label(color, label, marker='o'):
    return mlines.Line2D(
        [], [], 
        marker=marker,
        color=color,
        linestyle='None',
        markersize=5, 
        label=label
    )

def main():
    print("Getting Embeddigns")
    embs_dict = get_embs()
    all_embs = embs_dict["emb"].numpy()

    print("Applying UMAP")
    reducer = umap.UMAP(
        n_neighbors=NEIGHBORS
    )
    all_embs:np.ndarray = reducer.fit_transform(all_embs) # type: ignore

    print("Ploting")
    plt.rcParams["figure.figsize"] = (15, 10)
    # for x, y, m, c in zip(all_embs[:,0], all_embs[:,1], embs_dict["genre_mkr"], embs_dict["game_color"]):
    #     plt.plot(x, y, color=c, marker=m, markersize=3)
    for x, y, c in zip(all_embs[:,0], all_embs[:,1], embs_dict["game_color"]):
        plt.plot(x, y, color=c, marker='o', markersize=3)

    plt.title(f'CLAP Embeddings for MAPPED DOWNSAMPLED Soundtracks Color Coded by Genre | N={NEIGHBORS}')
    plt.legend(
        handles=[maerker_label(color, label) for color, label in zip(COLORS, GENRES)], 
        bbox_to_anchor=(1, 1), 
        loc='upper left'
    )
    plt.tight_layout()

    print("Saving Plot")
    plt.savefig(f"./imgs/mapped_down_audio_embeddings_n_{NEIGHBORS}_rpg.png", bbox_inches='tight', dpi=600)

if __name__ == "__main__":
    main()
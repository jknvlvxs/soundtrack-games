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
DEEP_SEEK_GENRES = "/app/dataset/deepseek_genres.csv"
GENRES = ["Shooters", "Sports", "Platform", "RPG", "Puzzle", "Action", "Fighting", "Strategy", "Simulation", "Adventure", "Racing"]

MARKERS = ['o', '^', "<", ">", "1", 's', "p", '*', "+", 'x', "d"]
CMAP = 'viridis'

cmap = matplotlib.colormaps[CMAP]
normalized_colors = np.linspace(0, 1, len(GENRES))
COLORS = [cmap(val) for val in normalized_colors]

def get_embs_paths(dataset_folder) -> dict[str, tp.Any]:
    files_dict = {
        "game_color":  [],
        #"genre_mkr": [],
        "emb": []
    }
    genres_df = pd.read_csv(DEEP_SEEK_GENRES)

    games_folders = sorted(os.listdir(dataset_folder))

    # cmap = matplotlib.colormaps[CMAP]
    # normalized_colors = np.linspace(0, 1, len(games_folders))
    # colors = [cmap(val) for val in normalized_colors]

    for game_folder in games_folders:
        game_genre = genres_df[genres_df['game_folder'] == game_folder]['game_genre'].to_list()

        if len(game_genre) == 0:
            continue

        game_genre = game_genre[0]

        audios_emb_folder = os.path.join(dataset_folder, game_folder, 'soundtracks_clap')

        if os.path.exists(audios_emb_folder):
            for emb_file in sorted(os.listdir(audios_emb_folder)):
                audios_emb_file_path = os.path.join(audios_emb_folder, emb_file)

                # game_idx = games_folders.index(game_folder)
                # files_dict["game_color"].append(colors[game_idx])

                #genre_idx = GENRES.index(game_genre)
                #files_dict["genre_mkr"].append(MARKERS[genre_idx])

                genre_idx = GENRES.index(game_genre)
                files_dict["game_color"].append(COLORS[genre_idx])

                files_dict["emb"].append(audios_emb_file_path)

    return files_dict

def get_embs() -> dict[str, tp.Any]:
    files_dict = get_embs_paths(DATASET_ROOT)

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
    reducer = umap.UMAP()
    all_embs:np.ndarray = reducer.fit_transform(all_embs) # type: ignore

    print("Ploting")
    plt.rcParams["figure.figsize"] = (15, 10)
    # for x, y, m, c in zip(all_embs[:,0], all_embs[:,1], embs_dict["genre_mkr"], embs_dict["game_color"]):
    #     plt.plot(x, y, color=c, marker=m, markersize=3)
    for x, y, c in zip(all_embs[:,0], all_embs[:,1], embs_dict["game_color"]):
        plt.plot(x, y, color=c, marker='o', markersize=3)

    plt.title('CLAP Embeddings for Soundtracks Color Coded by Genre')
    plt.legend(
        handles=[maerker_label(color, label) for color, label in zip(COLORS, GENRES)], 
        bbox_to_anchor=(1, 1), 
        loc='upper left'
    )
    plt.tight_layout()

    print("Saving Plot")
    plt.savefig("./audio_embeddings.png", bbox_inches='tight', dpi=600)

if __name__ == "__main__":
    main()
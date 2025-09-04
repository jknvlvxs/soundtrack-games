import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

SPLIT = "splits_50_40_10"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def save_txt(data, path):
    with open(path, "w") as f:
        f.write(tabulate(data, headers="keys", tablefmt="github"))


def plot_distribution(series, title, xlabel, ylabel, path):
    plt.figure(figsize=(10, 6))
    series.sort_values(ascending=False).plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot_videos_info.py")
    parser.add_argument("--downsampled", action="store_true", help="Use downsampled dataset")
    args = parser.parse_args()

    data_dir = "2. downsample" if args.downsampled else "1. get_videos_info"
    output_base = "downsample" if args.downsampled else "full"
    df = pd.read_csv(f"../{data_dir}/videos_info.csv")

    for p in ["soundtracks", "videos", f"{SPLIT}/train", f"{SPLIT}/eval", f"{SPLIT}/test"]:
        ensure_dir(os.path.join(output_base, p))

    # SOUNDTRACKS
    soundtracks_per_game = df.groupby("game_id")["soundtrack"].nunique().reset_index(name="num_soundtracks")
    soundtracks_stats = soundtracks_per_game["num_soundtracks"].describe()
    save_txt(soundtracks_per_game, f"{output_base}/soundtracks/soundtracks_per_game.txt")
    save_txt(pd.DataFrame(soundtracks_stats), f"{output_base}/soundtracks/soundtracks_stats.txt")

    soundtracks_per_genre = df.groupby("genre")["soundtrack"].nunique()
    save_txt(soundtracks_per_genre.reset_index(name="num_soundtracks"), f"{output_base}/soundtracks/soundtracks_per_genre.txt")
    plot_distribution(soundtracks_per_genre, "Soundtracks por Gênero", "Gênero", "Nº de Trilhas", f"{output_base}/soundtracks/soundtracks_distribution.png")

    # VIDEOS
    videos_per_game = df.groupby("game_id")["segment"].count().reset_index(name="num_videos")
    videos_stats = videos_per_game["num_videos"].describe()
    save_txt(videos_per_game, f"{output_base}/videos/videos_per_game.txt")
    save_txt(pd.DataFrame(videos_stats), f"{output_base}/videos/videos_stats.txt")

    videos_per_soundtrack_per_game = df.groupby(["game_id", "soundtrack"])["segment"].count().reset_index(name="num_videos")
    save_txt(videos_per_soundtrack_per_game, f"{output_base}/videos/videos_per_soundtrack.txt")

    videos_per_genre = df.groupby("genre")["segment"].count()
    save_txt(videos_per_genre.reset_index(name="num_videos"), f"{output_base}/videos/videos_per_genre.txt")
    plot_distribution(videos_per_genre, "Vídeos por Gênero", "Gênero", "Nº de Vídeos", f"{output_base}/videos/videos_distribution.png")

    # GENRES
    games_per_genre = df.groupby("genre")["game_id"].nunique().reset_index(name="num_games")
    save_txt(games_per_genre, f"{output_base}/games_per_genre.txt")

    # SPLITS
    for split in ["train", "eval", "test"]:
        split_games = []
        split_txt_path = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir, '3. split', SPLIT, split+'.txt'))

        with open(split_txt_path, 'r') as f:
            split_games = f.readlines()
        split_games = [game_name.strip() for game_name in split_games]

        df_split = df[df['game_id'].isin(split_games)]

        # per game
        videos_per_game = df_split.groupby("game_id")["segment"].count().reset_index(name="num_videos")
        videos_stats = videos_per_game["num_videos"].describe()
        save_txt(videos_per_game, f"{output_base}/{SPLIT}/{split}/videos_per_game.txt")
        save_txt(pd.DataFrame(videos_stats), f"{output_base}/{SPLIT}/{split}/videos_stats.txt")

        # per soundtrack
        videos_per_soundtrack_per_game = df_split.groupby(["game_id", "soundtrack"])["segment"].count().reset_index(name="num_videos")
        save_txt(videos_per_soundtrack_per_game, f"{output_base}/{SPLIT}/{split}/videos_per_soundtrack.txt")

        # per genre
        videos_per_genre = df_split.groupby("genre")["segment"].count()
        save_txt(videos_per_genre.reset_index(name="num_videos"), f"{output_base}/{SPLIT}/{split}/videos_per_genre.txt")
        plot_distribution(videos_per_genre, "Vídeos por Gênero", "Gênero", "Nº de Vídeos", f"{output_base}/{SPLIT}/{split}/videos_distribution.png")

import json
import pandas as pd

def downsample(df):
    # Remover jogos com menos de 60 vídeos
    game_counts = df["game_id"].value_counts()
    valid_games = game_counts[game_counts >= 60].index
    df = df[df["game_id"].isin(valid_games)]

    # Garantir ao menos 1 vídeo por soundtrack de cada jogo
    keep_rows = []

    for (game_id, soundtrack), group in df.groupby(["game_id", "soundtrack"]):
        selected = group.sample(n=1, random_state=42)
        keep_rows.append(selected)

    keep_df = pd.concat(keep_rows)

    # Agora vamos balancear os jogos restantes
    remaining_df = df[~df.index.isin(keep_df.index)]
    videos_per_game = remaining_df.groupby("game_id").size()

    # Tentar minimizar a diferença de vídeos entre jogos
    min_videos = videos_per_game.min()

    # Amostragem balanceada
    balanced_rows = []
    for game_id, group in remaining_df.groupby("game_id"):
        n = min(min_videos, len(group))
        sampled = group.sample(n=n, random_state=42)
        balanced_rows.append(sampled)

    balanced_df = pd.concat(balanced_rows)

    # Combinar com os vídeos obrigatórios
    final_df = pd.concat([keep_df, balanced_df]).drop_duplicates()
    return final_df.reset_index(drop=True)


selected_segments = set()

with open('selected_videos.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line)
        video_path = data['video_description_path']
        segment = video_path.split('/')[-1]  # Get the filename (e.g., 3-ninjas-kick-back_00005.mp4)
        selected_segments.add(segment)

df = pd.read_csv("../get_videos_info/videos_info.csv")
filtered_df = downsample(df[df["segment"].isin(selected_segments)])
filtered_df.to_csv('videos_info.csv', index=False)

import pandas as pd
import numpy as np


def calcular_pesos_genero(genre_counts, scaling_factor=1.5):
    # Define o número alvo uniforme (baseado no menor gênero * fator)
    uniform_target = int(genre_counts.min() * scaling_factor)

    # Calcula pesos como razão entre alvo e atual, com máximo 1.0 (só downsample)
    return (uniform_target / genre_counts).clip(upper=1.0).to_dict()


def downsample(df, num_segments_per_soundtrack=5, percentile=80):
    # Remover jogos com menos de 60 segmentos
    game_counts = df["game_id"].value_counts()
    valid_games = game_counts[game_counts >= 60].index
    df = df[df["game_id"].isin(valid_games)]

    # Calcula os pesos para cada gênero
    genre_counts = df["genre"].value_counts()
    genre_weights = calcular_pesos_genero(genre_counts)

    # Calcula o quantil definido para número de soundtracks por jogo
    soundtrack_counts = df.groupby("game_id")["soundtrack"].nunique()
    s = int(np.percentile(soundtrack_counts.values, percentile))  # ex: 80% das trilhas têm até s

    dfs = []

    # Agrupa por jogo
    for game_id, game_group in df.groupby("game_id"):
        p = genre_weights.get(game_group["genre"].iloc[0], 1.0)  # peso para o gênero
        numero_minimo = int(s * num_segments_per_soundtrack * p)

        # Número de trilhas sonoras no jogo
        soundtracks = game_group["soundtrack"].unique()

        # Quantos segmentos por trilha?
        v = max(int(numero_minimo / len(soundtracks)), 1)

        # Para cada trilha, faz a amostragem linear
        for soundtrack in soundtracks:
            segments = game_group[game_group["soundtrack"] == soundtrack].sort_values(by="segment")

            if len(segments) <= v:
                sampled = segments
            else:
                # Ignora o primeiro e o último segmento
                indices = np.linspace(0, len(segments) - 1, v + 2, dtype=int)
                sampled = segments.iloc[indices[1:-1]]

            dfs.append(sampled)

    # Junta tudo
    return pd.concat(dfs).reset_index(drop=True)


df = pd.read_csv("../get_videos_info/videos_info.csv")
filtered_df = downsample(df)
filtered_df = filtered_df.sort_values(by=["game_id", "soundtrack"])
filtered_df.to_csv("videos_info.csv", index=False)

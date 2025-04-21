import pandas as pd
import numpy as np


def downsample(df, num_segments_per_soundtrack=5, percentile=80):
    # Calcular número de vídeos por gênero
    genre_counts = df["genre"].value_counts()
    max_videos = genre_counts.max()
    min_videos = genre_counts.min()

    # Peso inversamente proporcional à quantidade de vídeos
    genre_weights = ((max_videos - genre_counts) / (max_videos - min_videos)).to_dict()

    # Calcular o quantil de 80% das soundtracks por jogo (s)
    soundtrack_counts = df.groupby("game_id")["soundtrack"].nunique()
    s = int(np.percentile(soundtrack_counts.values, percentile))

    dfs = []

    # Agrupar por jogo
    for game_id, game_group in df.groupby("game_id"):
        genre = game_group["genre"].iloc[0]
        p = genre_weights.get(genre, 1.0)
        numero_minimo = int(s * num_segments_per_soundtrack * p)

        soundtracks = game_group["soundtrack"].unique()
        ns = len(soundtracks)
        v = max(int(numero_minimo / ns), 1)

        # Processar cada soundtrack
        for soundtrack in soundtracks:
            segment_group = game_group[game_group["soundtrack"] == soundtrack].sort_values(by="segment")

            # Ignorar primeiro e último segmento
            segments = segment_group.iloc[1:-1]
            if len(segments) <= v:
                sampled = segments
            else:
                # Selecionar v índices linearmente espaçados
                indices = np.linspace(0, len(segments) - 1, v, dtype=int)
                sampled = segments.iloc[indices]
            dfs.append(sampled)

    return pd.concat(dfs).reset_index(drop=True)


df = pd.read_csv("../get_videos_info/videos_info.csv")
filtered_df = downsample(df)
filtered_df = filtered_df.sort_values(by=["game_id", "soundtrack"])
filtered_df.to_csv("videos_info.csv", index=False)

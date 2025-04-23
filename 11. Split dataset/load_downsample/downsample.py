import pandas as pd
import numpy as np

def remove_by_n_of_segments(df:pd.DataFrame, n_segments:int=60) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
        Remove games with less than n_segments segments.
        Defaults to 60 segments, or 10 minutes of gameplay).

        Returns:
            A df with the valid games and another with the invalid ones.
    """

    game_counts = df["game_id"].value_counts()

    valid_games = game_counts[game_counts >= n_segments].index
    valid_df = df[df["game_id"].isin(valid_games)]

    invalid_games = game_counts[game_counts < n_segments].index
    invalid_df = df[df["game_id"].isin(invalid_games)]

    return valid_df, invalid_df


def calculate_genres_weights(genre_counts:pd.DataFrame, scaling_factor:int=1.5) -> dict[str, float]:
    """
        Define the target uniform distribution given by:

            genre_with_smallest_num_of_segments * scaling_factor

        The scaling factor is a factor that determines how much we tolerate to deviate from the
        true uniform distribution we could have at the end.

        Then we divide such `uniform_target` by the amout of segments of each genre to get the weight `w`

        `w` now indicates how we should downsample each genre

        Retuns:
            a dict in the form {`genre_name`: `genre_w`}
    """
    uniform_target = int(genre_counts.min() * scaling_factor)

    # clip to 1 since we are not performing data augmentation
    w_dict = (uniform_target / genre_counts).clip(upper=1.0).to_dict()

    return w_dict


def downsample(df:pd.DataFrame, num_segments_per_soundtrack:int=5, percentile:int=80):
    # TODO: commented because first of all we removed half of the segments and the csv do not contain
    # all seguiments for the given game (unmaped ones are ignored)
    # Second because I checked them by hand (4-nin-shougi and zootto-mahjong) and they are a complete
    # match of the game in question (shougi and mahjong), so they are complete gameplays in a sense

    #df, invalid_df = remove_by_n_of_segments(df)

    #print("The following games have less than 10min of gameplay:")
    #print(invalid_df.groupby('game_id').value_counts())

    # We need to downsample aiming to balance the genres, so we calculate a weight for each of them
    # The bigger the amount of segments for the genre the smaller the weight
    genre_counts = df["genre"].value_counts()

    genre_weights = calculate_genres_weights(genre_counts)

    # TODO: Remove?
    # Calculates the quantile defined for the number of soundtrack per game
    # ex: 80% of the soundtracks have s segments
    # This will be used as our base number to make the downsample. We will modify it with the genre weight
    #soundtrack_counts = df.groupby("game_id")["soundtrack"].nunique()
    #sgs_quantile = int(np.percentile(soundtrack_counts.values, percentile))

    dfs = []

    # Group per game and loop the game groups
    for game_id, game_group in df.groupby("game_id"):
        genre = game_group["genre"].iloc[0]
        genre_weight = genre_weights.get(genre, 1.0)
        n_game_segments = len(game_group)
        # The target number of segments we want to get for this game is the number of
        # segments it has times the weight of its genre
        # In the final sommation it will be as if we took the total number of segments of
        # the genre and multiplied by the genre weight, achieving our quasi-uniform target distribution
        n_game_segments = round(n_game_segments * genre_weight)

        # Now, we need to equally distribute this num_game_segments over the soundtracks of the game
        soundtracks = game_group["soundtrack"].unique()
        num_soundtracks = len(soundtracks)
        num_soundtrack_segments = n_game_segments // num_soundtracks
        # Granting that there is at least one segment per soundtrack
        num_soundtrack_segments = max(num_soundtrack_segments, 1)

        # Get num_soundtrack_segments segments for each soundtrack as linearly spaced in time as possible
        # TODO: We cant just utilize linspace because the segments are not linearly spaced
        # We need to use the number of the segment to get where it is in time
        for soundtrack in soundtracks:
            soundtrack_segments:pd.DataFrame = game_group[game_group["soundtrack"] == soundtrack].sort_values(by="segment")

            if len(soundtrack_segments) <= num_soundtrack_segments:
                sampled = soundtrack_segments
            else:
                # Sum +2 and then ignore the first and second segments sicne they probably are opening or endin screens
                indices = np.linspace(0, len(soundtrack_segments), num_soundtrack_segments +2, dtype=int)
                indices = indices[1:-1]

                assert num_soundtrack_segments == len(indices), f"{game_id}: num_soundtrack_segments {num_soundtrack_segments} differs from selected indicies in linspace {len(indices)}"

                sampled = soundtrack_segments.iloc[indices]

            dfs.append(sampled)

    # Junta tudo
    return pd.concat(dfs).reset_index(drop=True)

def main():
    df = pd.read_csv("../get_videos_info/videos_info.csv")
    filtered_df = downsample(df)
    filtered_df = filtered_df.sort_values(by=["game_id", "soundtrack"])
    filtered_df.to_csv("videos_info.csv", index=False)

if __name__ == "__main__":
    main()
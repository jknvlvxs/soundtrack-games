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


def calculate_genres_weights(genre_counts:pd.DataFrame, scaling_factor:float=1.5) -> dict[str, float]:
    """
        Define the target uniform distribution given by:

            genre_with_smallest_num_of_segments * scaling_factor

        The scaling factor determines how much we tolerate to deviate from the true uniform distribution
        that would otherwise be purely based on the genre with less segments.

        Then we divide such `uniform_target` by the amout of segments of each genre to get the weight `w`

        `w` now indicates how we should downsample each genre

        Retuns:
            a dict in the form {`genre_name`: `genre_w`}
    """
    uniform_target = int(genre_counts.min() * scaling_factor) # TODO try with scaling_factor = 1

    # clip to 1 since we are not performing data augmentation
    w_dict = (uniform_target / genre_counts).clip(upper=1.0).to_dict()

    return w_dict


def downsample(df:pd.DataFrame):
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

    dfs = []
    count_less_than_required = 0

    # Group per game and loop the game groups
    for game_id, game_group in df.groupby("game_id"):
        genre = game_group["genre"].iloc[0]
        genre_weight = genre_weights.get(genre, 1.0)
        n_game_segments = len(game_group)

        # The target number of segments we want to get for this game is the number of
        # segments it has times the weight of its genre
        # In the final sommation it will be as if we took the total number of segments of
        # the genre and multiplied by the genre weight, achieving our uniform_target
        tgt_game_segments = round(n_game_segments * genre_weight)

        # Now, we need to equally distribute this tgt_game_segments over the soundtracks of the game
        soundtracks = game_group["soundtrack"].unique()
        num_soundtracks = len(soundtracks)
        tgt_soundtrack_segments = tgt_game_segments // num_soundtracks
        print(f"Game {game_id}: tgt_soundtrack_segments {tgt_soundtrack_segments} = {tgt_game_segments} // {num_soundtracks}")

        # Granting that there is at least one segment per soundtrack
        tgt_soundtrack_segments = max(tgt_soundtrack_segments, 1)

        # Get tgt_soundtrack_segments segments for each soundtrack as linearly spaced in time as possible
        # TODO: We cant just utilize linspace because the segments are not linearly spaced
        # We need to use the number of the segment to get where it is in time
        for soundtrack in soundtracks:
            soundtrack_segments:pd.DataFrame = game_group[game_group["soundtrack"] == soundtrack].sort_values(by="segment")

            # TODO here this soundtrack could have as little as one segment,
            # so this might be one of the reasons why the distribution is alterated
            if len(soundtrack_segments) < tgt_soundtrack_segments:
                sampled = soundtrack_segments

                print(f"For game {game_id}, {soundtrack} has {tgt_soundtrack_segments-len(soundtrack_segments)} less videos than required")
                count_less_than_required += tgt_soundtrack_segments - len(soundtrack_segments)
            else:
                # Sum +2 and then ignore the first and second segments sicne they probably are opening or endin screens
                indices = np.linspace(0, len(soundtrack_segments), tgt_soundtrack_segments +2, dtype=int)
                indices = indices[1:-1]

                assert tgt_soundtrack_segments == len(indices), f"{game_id}: tgt_soundtrack_segments {tgt_soundtrack_segments} differs from selected indicies in linspace {len(indices)}"

                sampled = soundtrack_segments.iloc[indices]

            dfs.append(sampled)

        print()
        print()

    print(f"Total less than required {count_less_than_required}")

    # Put it all together
    return pd.concat(dfs).reset_index(drop=True)

def main():
    df = pd.read_csv("../1. get_videos_info/videos_info.csv")
    filtered_df = downsample(df)
    filtered_df = filtered_df.sort_values(by=["game_id", "soundtrack"])
    filtered_df.to_csv("videos_info.csv", index=False)

if __name__ == "__main__":
    main()
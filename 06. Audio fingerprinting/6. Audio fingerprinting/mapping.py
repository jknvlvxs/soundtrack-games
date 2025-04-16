import os
import json
import argparse
import traceback
import ffmpeg
import sys

import mysql.connector

from tqdm import tqdm
from dejavu import Dejavu

from dejavu.logic.recognizer.file_recognizer import FileRecognizer


def init_database(db_config_path, console, game):
    try:
        with open(db_config_path) as f:
            config = json.load(f)

            mydb = mysql.connector.connect(
                host=config["database"]["host"],
                user=config["database"]["user"],
                password=config["database"]["password"],
            )

            database = console.replace("-", "_") + "_" + game.replace("-", "_").split("[")[0]

            config["database"]["database"] = database

            mycursor = mydb.cursor()
            mycursor.execute("CREATE DATABASE IF NOT EXISTS " + database + ";")
            mycursor.close()

            print(f"Created new database: {database}")
    except Exception as err:
        print(f"Failed to create database: {err}")
        raise err

    return Dejavu(config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="dejavu.py")
    # parser.add_argument("--dataset_root", type=str, default="../5. Database/", help="path for the dataset games folder")
    parser.add_argument("--dataset_root", type=str, default="/app/dataset/", help="path for the dataset games folder")
    parser.add_argument("--nprocesses", type=int, default=4, help="number of processes in fingerprint_directory function")
    parser.add_argument("--console", type=str, default="nintendo-snes-spc", help="selected console")
    args = parser.parse_args()

    dataset_path = args.dataset_root + args.console

    games_folders = sorted(os.listdir(dataset_path))
    n_games = len(games_folders)

    for game in tqdm(games_folders):
        djv = init_database("config.json", args.console, game)
        print("Total of fingerprints: ", djv.db.get_num_fingerprints())

        video_folder_path = os.path.join(dataset_path, game, "videos")
        game_videos = sorted(os.listdir(video_folder_path))

        soundtrack_folder_path = os.path.join(dataset_path, game, "soundtracks")
        game_soundtracks = sorted(os.listdir(soundtrack_folder_path))

        mapping_log_path = os.path.join(dataset_path, game, "mapping_log.csv")

        if os.path.exists(mapping_log_path):
            print(f"Mapping log already exists for {game}")
            continue

        try:
            tqdm.write(f"Generating fingerpint for game {game}")
            djv.fingerprint_directory(soundtrack_folder_path, [".mp3"], args.nprocesses)

            log_string = "video,soundtrack,input_confidence,fingerprinted_confidence\n"
            tqdm.write(log_string)
            with open(mapping_log_path, "w", encoding="UTF8") as f:
                f.write(log_string)

            # Mapping for each video
            for video in game_videos:
                video_path = os.path.join(video_folder_path, video)
                audio_path = video_path.replace(".mp4", ".mp3")

                tqdm.write(f"Extracting audio from video video: {video}")
                stream = ffmpeg.input(video_path)
                stream = ffmpeg.output(stream, audio_path, loglevel="quiet")
                ffmpeg.run(stream)

                results = djv.recognize(FileRecognizer, audio_path)
                os.remove(audio_path)

                if not len(results["results"]) > 0:
                    tqdm.write(f"No results found for video {video}")

                    with open(mapping_log_path, "a", encoding="UTF8") as f:
                        f.write(f"{video},None,None,None\n")
                    continue

                results = results["results"][0]
                song_name = results["song_name"].decode("utf-8")
                input_confidence = str(results["input_confidence"])
                fingerprinted_confidence = str(results["fingerprinted_confidence"])

                log_string = f"{video},{song_name},{input_confidence},{fingerprinted_confidence}\n"
                tqdm.write(log_string)
                with open(mapping_log_path, "a", encoding="UTF8") as f:
                    f.write(log_string)

                video_subfolder = os.path.join(video_folder_path, song_name)
                new_video_path = os.path.join(video_subfolder, video)

                if not os.path.exists(video_subfolder):
                    os.makedirs(video_subfolder)
                os.rename(video_path, new_video_path)

        except Exception as err:
            print(f"Error processing game {game}: {err}")
            os.remove(mapping_log_path)
            print(traceback.format_exc())

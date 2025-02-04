import os
import json
import argparse
import traceback
import ffmpeg
from tqdm import tqdm

import mysql.connector

from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer


def init(configpath:str, name_complement:str):
    """
        Load Dejavu config.
        Basic info is loaded from a JSON file located at configpath
        name_complement is the name o that database that will be created

        There will be one database per game, to avoid the scenario where 
        one video gets a soudtrack for the wrong game
    """
    try:
        with open(configpath) as f:
            config = json.load(f)

            mydb = mysql.connector.connect(
                host="localhost",
                user=config['database']["user"],
                password=config['database']["password"]
            )

            mycursor = mydb.cursor()

            database_name = config['database']["database"]+name_complement.replace("-", "_").split("[")[0]
            config['database']["database"] = database_name

            mycursor.execute("CREATE DATABASE "+database_name+";")
            mycursor.close()

            print(f"Created new database {database_name}")
    except IOError as err:
        print(f"Cannot open configuration: {str(err)}. Exiting") 
    except:
        print('Continuing....')

    # create a Dejavu instance
    return Dejavu(config)

def remove_db(configpath:str, name_complement:str):
    """
        Drop database for game with given configpath and name_complement
    """
    try:
        with open(configpath) as f:
            config = json.load(f)

            mydb = mysql.connector.connect(
                host="localhost",
                user=config['database']["user"],
                password=config['database']["password"]
            )

            mycursor = mydb.cursor()

            database_name = config['database']["database"]+name_complement.replace("-", "_").split("[")[0]

            mycursor.execute("DROP DATABASE "+database_name+";")
            mycursor.close()
    except IOError as err:
        print(f"Cannot open configuration: {str(err)}. Exiting")

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='dejavu.py')
    parser.add_argument('--config_file', type=str, default="./config.json", help="dejavu db configs json")
    parser.add_argument('--dataset_root', type=str, default="../5. Database/nintendo-snes-spc/", help="path for the dataset games folder")
    parser.add_argument('--n_processes', type=int, default=4, help="number of processes in fingerprint_directory function") 
    parser.add_argument('--remove_db', action="store_true", help="reset game database for each game', defaults to False'") 
    parser.add_argument('--remove_not_found', action="store_true", help="remove videos that had no soundtrack, if false this videos will be logged to the csv, defaults to False") 
    args = parser.parse_args()

    # Loop soundtracks
    games_folders = sorted(os.listdir(args.dataset_root))
    n_games = len(games_folders)

    counter = 0
    for game_folder in tqdm(games_folders, total=n_games):
        database_name_complement = f"_snes_{game_folder}"

        if args.remove_db:
            print(f"Removing the database for game {game_folder}")
            remove_db(args.config_file, database_name_complement)

        # Init Dejavu for this game
        djv = init(args.config_file, database_name_complement)
        print("Total of fingerprints: ", djv.db.get_num_fingerprints())

        counter += 1

        video_folder_path = os.path.join(args.dataset_root, game_folder, 'videos')
        game_videos = sorted(os.listdir(video_folder_path))

        soundtrack_folder_path = os.path.join(args.dataset_root, game_folder, 'soundtracks')
        game_soundtracks = sorted(os.listdir(soundtrack_folder_path))

        mapping_log_path = os.path.join(args.dataset_root, game_folder, 'mapping_log.csv')

        # Skip if already processed
        if os.path.exists(mapping_log_path):
            print(f"Skipping game {counter}: {game_folder}")
            continue

        try:
            # Get fingerprints for current game
            tqdm.write(f"Generating fingerprint for game {game_folder}")
            djv.fingerprint_directory(soundtrack_folder_path, [".mp3" ], args.n_processes)

            # Create a csv in each video folder to log mapping info
            log_string = "video,soundtrack,input_confidence,fingerprint_confidence\n"
            tqdm.write(log_string)
            with open(mapping_log_path, 'w', encoding='UTF8') as f:
                f.write(log_string)

            # Mapping for each video
            for video in game_videos:
                video_path = os.path.join(video_folder_path, video)
                audio_path = video_path[:-1]+"3" #.mp4 to .mp3

                # Get video's audio
                tqdm.write(f"Ffmeg extract audio from video {video}")
                stream = ffmpeg.input(video_path)
                stream = ffmpeg.output(stream, audio_path, loglevel="error")
                ffmpeg.run(stream)

                # Recognize audio
                results = djv.recognize(FileRecognizer, audio_path)

                # Remove created audio
                os.remove(audio_path)

                # If video has no soundtrack
                if not len(results['results']) > 0:
                    tqdm.write(f"No matches found for video {video_path}\n")

                    # Remove video or log it with None
                    if args.remove_not_found:
                        tqdm.write(f"Removing it from the dataset\n")
                        os.remove(video_path)
                    else:
                        with open(mapping_log_path, 'a', encoding='UTF8') as f:
                            f.write(f"{video},None,None,None\n")

                    continue

                # Log
                result = results['results'][0]
                song_name = result['song_name'].decode('utf-8')
                input_confidence = str(result['input_confidence'])
                fingerprinted_confidence = str(result['fingerprinted_confidence'])

                log_string = f"{video},{song_name},{input_confidence},{fingerprinted_confidence}\n"
                tqdm.write(log_string)

                with open(mapping_log_path, 'a', encoding='UTF8') as f:
                    f.write(log_string)

                # Move current game videos to a subfolder with the soundtrack name
                # game
                # |_videos
                #   |_sountrack_0001
                #     |_*videos with sountrack 1*
                video_subfolder = os.path.join(video_folder_path, song_name)
                new_video_path = os.path.join(video_subfolder, video)

                if not os.path.isdir(video_subfolder):
                    os.mkdir(video_subfolder)
                os.rename(video_path, new_video_path)

        except Exception as e:
            print(f'@@@ ERROR @@@ for game {counter}: {game_folder}')

            # in case of error we remove the log csv so the system will process this game again on the next run
            os.remove(mapping_log_path)

            print(traceback.format_exc())

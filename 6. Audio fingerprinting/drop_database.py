import os
import json
import argparse
import traceback
import ffmpeg
import sys
import shutil

import mysql.connector

from tqdm import tqdm
from dejavu import Dejavu


def restore_dataset(base_dir):
    for game in os.listdir(base_dir):
        game_path = os.path.join(base_dir, game)
        videos_path = os.path.join(game_path, "videos")

        if os.path.isdir(videos_path):
            for subdir in os.listdir(videos_path):
                soundtrack_path = os.path.join(videos_path, subdir)

                if os.path.isdir(soundtrack_path) and subdir.startswith("soundtrack_"):
                    for arquivo in os.listdir(soundtrack_path):
                        if arquivo.endswith(".mp4"):
                            src = os.path.join(soundtrack_path, arquivo)
                            dest = os.path.join(videos_path, arquivo)
                            shutil.move(src, dest)

                    os.rmdir(soundtrack_path)

            for arquivo in os.listdir(videos_path):
                if arquivo.endswith(".mp3"):
                    os.remove(os.path.join(videos_path, arquivo))

        mapping_log_path = os.path.join(game_path, "mapping_log.csv")
        if os.path.exists(mapping_log_path):
            os.remove(mapping_log_path)

def drop_database(db_config_path, console, game):
    try:
        with open(db_config_path) as f:
            config = json.load(f)

            mydb = mysql.connector.connect(
                host="localhost",
                user=config["database"]["user"],
                password=config["database"]["password"],
            )

            database = console.replace("-", "_") + "_" + game.replace("-", "_").split("[")[0]

            mycursor = mydb.cursor()
            mycursor.execute("DROP DATABASE IF EXISTS " + database + ";")
            mycursor.close()

            print(f"Droped database: {database}")
    except Exception as err:
        print(f"Failed to drop database: {err}")
        raise err


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="dejavu.py")
    # parser.add_argument("--dataset_root", type=str, default="../5. Database/", help="path for the dataset games folder")
    parser.add_argument("--dataset_root", type=str, default="/app/dataset/", help="path for the dataset games folder")
    parser.add_argument("--console", type=str, default="nintendo-snes-spc", help="selected console")
    args = parser.parse_args()

    dataset_path = args.dataset_root + args.console

    games_folders = sorted(os.listdir(dataset_path))
    n_games = len(games_folders)

    for game in tqdm(games_folders):
        drop_database("config.json", args.console, game)

    # confirm_restore = input("Você TEM CERTEZA que deseja restaurar a base de dados? (y/n): ")

    # if confirm_restore.lower() != "y":
    #     print("Restauração cancelada.")
    #     exit()

    restore_dataset(dataset_path)

import os
import json
import argparse
import traceback
import ffmpeg
import sys

import mysql.connector

from tqdm import tqdm
from dejavu import Dejavu


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
    parser.add_argument("--console", type=str, default="nintendo-snes-spc", help="selected console")
    args = parser.parse_args()

    dataset_path = f"../5. Database/{args.console}"

    games_folders = sorted(os.listdir(dataset_path))
    n_games = len(games_folders)

    for game in tqdm(games_folders):
        drop_database("config.json", args.console, game)

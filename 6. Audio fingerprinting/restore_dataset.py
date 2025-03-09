import os
import shutil
import argparse

def restore_db(base_dir):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="restore_dataset.py")
    # parser.add_argument("--dataset_root", type=str, default="../5. Database/", help="path for the dataset games folder")
    parser.add_argument("--dataset_root", type=str, default="/app/dataset/", help="path for the dataset games folder")
    parser.add_argument("--console", type=str, default="nintendo-snes-spc", help="selected console")
    args = parser.parse_args()

    base_directory = args.dataset_root + args.console

    confirm_restore = input("Você TEM CERTEZA que deseja restaurar a base de dados? (y/n): ")

    if confirm_restore.lower() != 'y':
        print('Restauração cancelada.')
        exit()

    restore_db(base_directory)

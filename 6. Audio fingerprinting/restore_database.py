import os
import shutil


def restore_db(base_dir):
    for game in os.listdir(base_dir):
        game_path = os.path.join(base_dir, game)
        videos_path = os.path.join(game_path, "videos")

        if not os.path.isdir(videos_path):
            continue

        for subdir in os.listdir(videos_path):
            soundtrack_path = os.path.join(videos_path, subdir)

            if os.path.isdir(soundtrack_path) and subdir.startswith("soundtrack_"):
                for arquivo in os.listdir(soundtrack_path):
                    if arquivo.endswith(".mp4"):
                        src = os.path.join(soundtrack_path, arquivo)
                        dest = os.path.join(videos_path, arquivo)
                        shutil.move(src, dest)

                os.rmdir(soundtrack_path)

        mapping_log_path = os.path.join(game_path, "mapping_log.csv")
        if os.path.exists(mapping_log_path):
            os.remove(mapping_log_path)


if __name__ == "__main__":
    path = os.path.dirname(__file__)
    base_dir = os.path.join(path, "")
    base_directory = path + "/../5. Database/nintendo-snes-spc"

    confirm_restore = input("Você TEM CERTEZA que deseja restaurar a base de dados? (y/n): ")
    
    if confirm_restore.lower() != 'y':
        print('Restauração cancelada.')
        exit()

    restore_db(base_directory)

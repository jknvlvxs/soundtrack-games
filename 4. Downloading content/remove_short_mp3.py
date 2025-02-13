import os
from mutagen.mp3 import MP3


def deletar_mp3s(base_dir):
    for jogo in os.listdir(base_dir):
        jogo_path = os.path.join(base_dir, jogo)
        soundtracks_path = os.path.join(jogo_path, "soundtracks")

        if os.path.isdir(soundtracks_path):
            for arquivo in os.listdir(soundtracks_path):
                if arquivo.startswith("soundtrack_") and arquivo.endswith(".mp3"):
                    file_path = os.path.join(soundtracks_path, arquivo)
                    try:
                        audio = MP3(file_path)
                        if audio.info.length < 8:
                            print(f"{jogo}/soundtracks/{arquivo}")
                            os.remove(file_path)
                    except Exception as e:
                        print(f"Erro ao processar {file_path}: {e}")


if __name__ == "__main__":
    path = os.path.dirname(__file__)
    base_dir = os.path.join(path, "")
    base_directory = path + "/../5. Database/nintendo-snes-spc"

    confirm_restore = input("Você TEM CERTEZA que deseja remover os arquivos .mp3 com duração menor que 8 segundos? (y/n): ")
    
    if confirm_restore.lower() != 'y':
        print('Remoção cancelada.')
        exit()

    deletar_mp3s(base_directory)

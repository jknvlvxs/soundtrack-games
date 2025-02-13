import os

def eliminate_half(base_dir):
    for jogo in os.listdir(base_dir):
        jogo_path = os.path.join(base_dir, jogo)
        videos_path = os.path.join(jogo_path, "videos")

        if os.path.isdir(videos_path):
            for arquivo in os.listdir(videos_path):
                file_path = os.path.join(videos_path, arquivo)
                
                try:
                    video_number = int(arquivo[-9:-4])
                    if video_number % 2 == 0:
                        print(file_path)
                        os.remove(file_path)
                except ValueError:
                    print(f"Erro ao processar {file_path}: formato de nome inesperado")


if __name__ == "__main__":
    path = os.path.dirname(__file__)
    base_directory = os.path.join(path, "../5. Database/nintendo-snes-spc")
    
    confirm_delete = input("Você TEM CERTEZA que deseja remover os arquivos de vídeo pares? (y/n): ")
    
    if confirm_delete.lower() != 'y':
        print('Remoção cancelada.')
        exit()
    
    eliminate_half(base_directory)

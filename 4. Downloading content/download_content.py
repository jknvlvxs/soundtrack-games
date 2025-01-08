import os
import json
import requests
import shutil
import py7zr
from pytubefix.cli import on_progress
from pytubefix import YouTube
from zipfile import ZipFile
from tqdm import tqdm

path = os.path.dirname(__file__)
base_dir = os.path.join(path, "")
data_file = os.path.join(path + "/../3. Collecting Youtube Links/", "data.json")


# Função para criar uma pasta, se ela não existir
def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Função para baixar arquivos a partir de uma URL
def download_file(url, path, name):
    print(f"\nBaixando {name}")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get("Content-Length", 0))
        block_size = 1024  # Tamanho do bloco em bytes

        # Barra de progresso
        with open(path, "wb") as file, tqdm(
            desc=name,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                file.write(data)
                bar.update(len(data))  # Atualiza a barra de progresso

        print(f"→ Download concluído: {path}")
    else:
        print(f"→ Erro ao baixar {url}")


# Função para extrair arquivos .zip e .7z
def extract_archive(file_path, extract_to):
    print(f"→ Extraindo arquivos de trilha sonora")
    if file_path.endswith(".zip"):
        with ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
    elif file_path.endswith(".7z"):
        with py7zr.SevenZipFile(file_path, "r") as archive:
            archive.extractall(extract_to)
    print(f"→ Extração concluída em: {extract_to}")


# Função para baixar vídeos do YouTube
def download_youtube_video(url, path):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        print(f"→ Baixando vídeo do YouTube: '{yt.title}'")

        video_stream = yt.streams.get_lowest_resolution()

        if video_stream:
            video_stream.download(output_path=path)
            print(f"→ Vídeo do YouTube baixado em: {path}")
        else:
            print("→ Nenhum stream disponível para download.")

    except Exception as e:
        print(f"Erro ao baixar vídeo do YouTube: {e}")


# Carregar dados do JSON
with open(data_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Processar cada item no JSON
for item in data:
    # Extrair o nome do jogo para criar a pasta
    game_name = item["name"].split(" (")[0]
    game_folder = os.path.join("../5. Database", game_name)

    # Criar as pastas do jogo
    create_folder(game_folder)
    soundtracks_folder = os.path.join(game_folder, "soundtracks")
    videos_folder = os.path.join(game_folder, "videos")
    create_folder(soundtracks_folder)
    create_folder(videos_folder)

    # Baixar e extrair o arquivo de som
    if not os.listdir(soundtracks_folder):
        soundtrack_url = item["url"]
        soundtrack_file_path = os.path.join(
            soundtracks_folder, os.path.basename(soundtrack_url)
        )
        download_file(soundtrack_url, soundtrack_file_path, game_name)
        extract_archive(soundtrack_file_path, soundtracks_folder)
        os.remove(soundtrack_file_path)  # Remove o arquivo compactado após a extração

    # Baixar e salvar o vídeo do YouTube
    if not os.listdir(videos_folder):
        youtube_url = item["youtube"]["url"]
        download_youtube_video(youtube_url, videos_folder)

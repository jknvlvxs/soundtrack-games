import os
import subprocess
import sys
import json
import requests
import shutil
import py7zr
import ffmpeg
from concurrent.futures import ThreadPoolExecutor
from pytubefix.cli import on_progress
from pytubefix import YouTube
from zipfile import ZipFile
from tqdm import tqdm

path = os.path.dirname(__file__)
base_dir = os.path.join(path, "")
data_file = os.path.join(path + "/../3. Collecting youtube links/zophar/", "metadata.json")


# Função para criar uma pasta, se ela não existir
def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print(f"Pasta já existe: {path}")


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

    os.remove(file_path)  # Remove o arquivo compactado após a extração

    # Renomear todos os arquivos extraídos para "soundtrack_00X"
    for i, file in enumerate(os.listdir(extract_to)):
        os.rename(
            os.path.join(extract_to, file),
            os.path.join(
                extract_to, f"soundtrack_{i+1:04d}{os.path.splitext(file)[1]}"
            ),
        )

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

def slice_video_into_frames(video_path, game_name):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"File not found: {video_path}")

    video_dir = os.path.dirname(video_path)
    video_name = os.path.basename(video_path)
    video_name_without_ext, video_ext = os.path.splitext(video_name)
    output_template = os.path.join(video_dir, f"{game_name}_%05d{video_ext}")

    # Use ffmpeg to slice the video into 10-second frames
    try:
        (
            ffmpeg.input(video_path)
            .output(output_template, f="segment", segment_time=10, reset_timestamps=1, g=30)
            .run(overwrite_output=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Error slicing video: {e.stderr.decode()}") from e

    # Delete the original video
    try:
        os.remove(video_path)
    except OSError as e:
        raise RuntimeError(f"Error deleting original video: {e}")

    print(f"Video sliced successfully and original video deleted. Slices saved as: {output_template}") 


# Carregar dados do JSON
with open(data_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Filtrar data para teste
# filter_games = ["top-anglers-super-fishing-big-fight-2"]
filter_games = ["top-gear", "toy-story-1996"]
data = [item for item in data if item["slug"] in filter_games]

# Filtrar data por console via argumento
# data = [item for item in data if item["system"] == sys.argv[1]]

# Filtrar objetos sem atributo "youtube"
data = [item for item in data if "youtube" in item]

# Processar cada item no JSON
for item in data:
    # Extrair o nome do jogo para criar a pasta
    console_name = item["system"]
    game_name = item["slug"]
    game_folder = os.path.join("5. Database", console_name, game_name)

    # Criar as pastas do jogo
    create_folder(game_folder)
    soundtracks_folder = os.path.join(game_folder, "soundtracks")
    videos_folder = os.path.join(game_folder, "videos")
    create_folder(soundtracks_folder)
    create_folder(videos_folder)
    
    def process_soundtracks(soundtracks_folder, soundtrack_url, game_name):
        # Baixar e extrair o arquivo de som
        if not os.listdir(soundtracks_folder):
            soundtrack_file_path = os.path.join(soundtracks_folder, os.path.basename(soundtrack_url))
            download_file(soundtrack_url, soundtrack_file_path, game_name)
            extract_archive(soundtrack_file_path, soundtracks_folder)

    def process_videos(videos_folder, youtube_url, game_name):
        # Baixar e salvar o vídeo do YouTube
        if not os.listdir(videos_folder):
            download_youtube_video(youtube_url, videos_folder)

            # Cortar vídeo em frames de 10 segundos
            video_path = os.path.join(videos_folder, os.listdir(videos_folder)[0])
            slice_video_into_frames(video_path, game_name)
            
    with ThreadPoolExecutor() as executor:
        executor.submit(process_soundtracks, soundtracks_folder, item["url"], game_name)
        executor.submit(process_videos, videos_folder, item["youtube"]["url"], game_name)

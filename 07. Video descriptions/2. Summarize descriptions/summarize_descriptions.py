import os
import time
import atexit
import logging
import requests
import argparse
import traceback
import coloredlogs
import typing as tp
from concurrent.futures import ProcessPoolExecutor

from tqdm import tqdm

import torch
from transformers import RobertaTokenizer

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer

from ollama_scout_api import OllamaChat

SEED = 42
session: requests.Session

class Config():
    def __init__(self, prompt:str, video_desc_path:str, descs_sum_path:str) -> None:
        self.prompt=prompt
        self.video_desc_path=video_desc_path
        self.descs_sum_path=descs_sum_path

MULTI_GENRE = Config(
    prompt="You will receive a description of a gameplay video. Your task will be to summarize such video description. You should mention the main genre of the game. Your answer should start describing the video right away. Avoid expressions like 'The video appears to be...' or 'The video shows..', since they don't mean anything and would just make the answer longer.",
    video_desc_path="videos_descriptions_mg",
    descs_sum_path="descs_sums_mg"
)

CONFIG = MULTI_GENRE

class Tokenizer:
    def __init__(self) -> None:
        self.tokenizer:RobertaTokenizer = RobertaTokenizer.from_pretrained('roberta-base')

    def tokenize(self, texts: tp.Union[str, tp.List[str]]):
        # we use the default params from CLAP module here as well
        return self.tokenizer(texts, padding="max_length", truncation=True, max_length=77, return_tensors="pt")

    def decode(self, token_ids):
        return self.tokenizer.decode(token_ids, skip_special_tokens=True)

def get_descriptions_paths(dataset_folder):
    g_loger = logging.getLogger('global_logger')

    files = []
    skiped = 0
    for game_folder in sorted(os.listdir(dataset_folder)):
        videos_descriptions_folder = os.path.join(dataset_folder, game_folder, CONFIG.video_desc_path)
        descs_sums_folder = os.path.join(dataset_folder, game_folder, CONFIG.descs_sum_path)

        if os.path.exists(videos_descriptions_folder):
            for video_description_file in sorted(os.listdir(videos_descriptions_folder)):
                video_description_file_path = os.path.join(videos_descriptions_folder, video_description_file)
                desc_sum_file_path = os.path.join(descs_sums_folder, video_description_file)

                if not os.path.exists(desc_sum_file_path):
                    files.append((video_description_file_path, desc_sum_file_path))
                else:
                    print(f"SKIPING {video_description_file_path}")
                    skiped += 1

    g_loger.info(f"SKIPED {skiped}")

    return files

def init_process():
    global session
    session = requests.Session()
    atexit.register(session.close)

def get_video_description_from_file(file:str) -> str:
    with open(file) as f:
        return f.read()

def apply_classic_nlp(text):
    # Remove ponctuation
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    tokens = " ".join(tokens)

    # Remove Stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(tokens)
    tokens = [word for word in tokens if word.lower() not in stop_words]

    return " ".join(tokens)

def run_ollama(videos_process:tuple[int, int, Tokenizer, list[tuple[str, str]]]):
    """
        Run inference in DeepSeek R1 on a set of videos descriptions, to get a music description

        Args:
            video_process: a tuple containing a int to identify the process and a list of tuples with the video description path and the music description path

        Will create a folder called music_descriptions in the videos parent dir containing the descricriptions in txt files with the same name
        as the videos descriptions files
    """
    pid, n_tokens, tokenizer, videos_paths = videos_process
    g_loger = logging.getLogger('global_logger')

    g_loger.info(f"Process {pid} with {len(videos_paths)} videos, from {videos_paths[0][0].split('/')[-1]} to {videos_paths[-1][0].split('/')[-1]}")

    video_description_path = ""
    current_idx = 0
    try:
        chat = OllamaChat(SEED, 1)
        res = chat.send(
                CONFIG.prompt,
                setup=True
            )

        for current_idx, descriptions_paths in tqdm(enumerate(videos_paths), total=len(videos_paths), desc=f'Process {pid}'):
            video_description_path, desc_sum_path = descriptions_paths

            descs_sums_folder = os.path.abspath(os.path.join(desc_sum_path, os.path.pardir))

            if not os.path.isdir(descs_sums_folder):
                os.mkdir(descs_sums_folder)

            # Get video description and generated music description
            video_description = get_video_description_from_file(video_description_path)

            desc_sum = chat.send(video_description, n_tokens)
            desc_sum_nlp = apply_classic_nlp(desc_sum)

            tokenized = tokenizer.tokenize(desc_sum_nlp)['input_ids'].squeeze(dim=0) # type: ignore
            decoded = tokenizer.decode(tokenized)

            with open(desc_sum_path, "w") as file:
                file.write(decoded)

            percentage = round(len(decoded)/len(desc_sum_nlp) * 100, 2)
            failed = percentage < 100

            video_desc_name = video_description_path.split('/')[-1]
            log_func = g_loger.critical if failed else g_loger.info
            log_func(f"\n{video_desc_name}:\nSummarized NLP: {desc_sum_nlp}\n\nDecoded: {decoded}\n\nDecoded is {percentage}% of the original\n")

    except Exception as e:
        g_loger.critical(f"Error in process {pid} for video at idx {current_idx}: {video_description_path}")
        g_loger.critical(traceback.format_exc())


if __name__ == '__main__':
    # Logger
    logging.basicConfig(
        filename="logs.log",
        filemode='a',
        encoding='utf-8'
    )

    g_loger = logging.getLogger('global_logger')

    coloredlogs.install(
        fmt = "{name} | {asctime}:{msecs:.0f} | {message}",
        style="{",
        datefmt="%m/%d %H:%M:%S",
    )

    # Parse arguments
    parser = argparse.ArgumentParser(description='summarize_descriptions.py')
    parser.add_argument('--dataset_root', type=str, default="/home/es119256/dados/datasets/vmdb_2/nintendo-snes-spc", help="path for the dataset games folder")
    parser.add_argument('--n_tokens', type=int, default=100, help="max number of tokens setted in Ollama")
    parser.add_argument('--n_processes', type=int, default=30, help="number of processes to run in parallel setted in OLLAMA_MAX_LOADED_MODELS inside the Ollama container") 
    args = parser.parse_args()

    # Download NLTK data
    nltk.download('stopwords')

    # Collect videos descriptions
    videos_paths = get_descriptions_paths(args.dataset_root) # list of tuples with the video description path and the summarized description path
    n_videos = len(videos_paths)
    n_tokens = args.n_tokens

    g_loger.info(f"N VIDEOS {n_videos} | N TOKENS {n_tokens}")

    lin_div = torch.linspace(0, n_videos, args.n_processes+1, dtype=int).tolist() # type: ignore

    videos_process_list:list[tuple[int, int, Tokenizer, list[tuple[str, str]]]] = [] # list to wrap a list of videos per process

    # Create Roberta Tokenizer instance
    tokenizer = Tokenizer()

    # Split games across processes
    for idx in range(len(lin_div)-1):
        videos_process_list.append(
            (idx, n_tokens, tokenizer, videos_paths[lin_div[idx]:lin_div[idx+1]])
        )

    g_start_time = time.perf_counter()

    # Create processes
    with ProcessPoolExecutor(initializer=init_process) as executor:
        futures = [executor.submit(run_ollama, video_process) for video_process in videos_process_list]

    g_elapsed_time = time.perf_counter() - g_start_time

    g_loger.info(f"\n\nIt took: {g_elapsed_time}")
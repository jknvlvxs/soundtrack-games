# ################################################################################################################ 
# When generating the Videos Descriptions we allowed Video Llama 3 free to generate answers as long as it wanned
# The problem is that it is very often larger than the 77 tokens context limit of Roberta used by LAION-CLAP
# LAION-CLAP is used to evaluate the model in MusicGen in their text consistency metric
# Also, sometimes it is ever larger than the context of T5-base used by MusicGen to encode text
# This code leverages Llama 4 Maveric to summarize the videos descriptions, limiting the amount of tokens in such 
# a way that it don't suspasses the 77 Roberta tokens used by LAION-CLAP
# ################################################################################################################ 
import os
import time
import random
import logging
import coloredlogs
import requests
import traceback
import typing as tp

import numpy as np
from tqdm import tqdm
from transformers import RobertaTokenizer

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer

from ollama_scout_api import OllamaChat

ROOT = "/home/es119256/dados/datasets/vmdb_2/nintendo-snes-spc"
N_DESCS = 1000
SEED = 42
N_TOKENS = 100

N_CHARS_LIST = []

session: requests.Session

class Config():
    def __init__(self, prompt:str, video_desc_path:str) -> None:
        self.prompt=prompt
        self.video_desc_path=video_desc_path

MULTI_GENRE = Config(
    prompt="You will receive a description of a gameplay video. Your task will be to summarize such video description. You should mention the main genre of the game. Your answer should start describing the video right away. Avoid expressions like 'The video appears to be...' or 'The video shows..', since they don't mean anything and would just make the answer longer.",
    video_desc_path="videos_descriptions_mg"
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

def get_descriptions_paths(dataset_folder) -> tp.List[str]:
    """
        Returns:
            List of video description paths
    """
    files = []

    for game_folder in os.listdir(dataset_folder):
        videos_descriptions_folder = os.path.join(dataset_folder, game_folder, CONFIG.video_desc_path)

        if os.path.exists(videos_descriptions_folder):
            for video_description_file in os.listdir(videos_descriptions_folder):
                video_description_file_path = os.path.join(videos_descriptions_folder, video_description_file)

                files.append(video_description_file_path)

    return files

def get_video_description_from_file(file:str) -> str:
    with open(file) as f:
        return f.read()

def format_ollama_res(res:str) -> str:
    answer = res.split('<answer>')[1]
    answer = answer.split('</answer>')[0]

    return answer

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

def run_ollama(videos_paths:list[str], tokenizer:Tokenizer, n_tokens:int) -> int:
    """
        Tests inference on Llama4:Scout on a set of videos descriptions in order to summarize them and check if the summarization exceeds 77 Roberta tokens

        Args:
            video_process: a tuple containing a int to identify the process and a list of tuples with the video description path and the music description path
            tokenizer: instance of Tokenizer to manage the Roberta Tokenizer

        Returns:
            current_idx:
                * If Roberta Tokenizer needs to truncate the summarization
                * At the end of the function
            -1:
                * If there is an exception
    """
    global N_CHARS_LIST

    g_loger = logging.getLogger('global_logger')

    video_description_path = ""
    current_idx = 0
    try:
        chat = OllamaChat(SEED, 1)
        res = chat.send(
                CONFIG.prompt,
                setup=True
            )

        for current_idx, video_description_path in tqdm(enumerate(videos_paths), total=len(videos_paths)):
            # Get video description and generated music description
            video_description = get_video_description_from_file(video_description_path)

            desc_sum = chat.send(video_description, n_tokens)
            desc_sum_nlp = apply_classic_nlp(desc_sum)
            #desc_sum = format_ollama_res(res)

            tokenized = tokenizer.tokenize(desc_sum_nlp)['input_ids'].squeeze(dim=0) # type: ignore
            decoded = tokenizer.decode(tokenized)
            N_CHARS_LIST.append(len(decoded))

            percentage = round(len(decoded)/len(desc_sum_nlp) * 100, 2)
            failed = percentage < 100

            video_desc_name = video_description_path.split('/')[-1]
            log_func = g_loger.critical if failed else g_loger.info
            log_func(f"\n{video_desc_name}:\nOriginal: {video_description}\nSummarized: {desc_sum}\n\n\nSummarized NLP: {desc_sum_nlp}\n\nDecoded: {decoded}\n\nDecoded is {percentage}% of the original\n")

            if failed:
                return current_idx

    except Exception as e:
        g_loger.critical(f"Error for video desc at idx {current_idx}: {video_description_path}")
        g_loger.critical(traceback.format_exc())
        return -1

    return current_idx

def get_chars_stas():
    n_chars_list = np.array(N_CHARS_LIST)
    mean_chars = n_chars_list.mean()
    std_chars = n_chars_list.std()

    return mean_chars, std_chars

def main():
    global N_TOKENS
    random.seed(SEED)
    nltk.download('stopwords')
    nltk.download('punkt_tab')

    # Collect videos descriptions
    descs_paths = get_descriptions_paths(ROOT)

    chosen_descs_paths = random.choices(descs_paths, k=N_DESCS)
    tokenizer = Tokenizer()

    g_loger.info(f"Chosen videos {N_DESCS}")

    g_start_time = time.perf_counter()

    first_run = True
    current_idx = 0
    while current_idx < N_DESCS-1:
        # Since run_ollama returns its current index counting from 0, we dont need to 
        # subtract it by 1 to continue from the description that failed  
        res = run_ollama(chosen_descs_paths[current_idx:], tokenizer, N_TOKENS)

        if res < 0:
            return

        current_idx += res

        if not first_run:
            N_TOKENS -= 1

            g_elapsed_time = time.perf_counter() - g_start_time

            mean, std = get_chars_stas()
            g_loger.critical(f"\nFAILED WITH {N_TOKENS} at idx {current_idx} | N CHARS: {mean}+-{std} | It took: {g_elapsed_time}")

        first_run = False

    g_elapsed_time = time.perf_counter() - g_start_time
    mean, std = get_chars_stas()
    g_loger.info(f"\n\nSUCCESS WITH {N_TOKENS} | N CHARS: {mean}+-{std} | It took: {g_elapsed_time}")

if __name__ == '__main__':
    logging.basicConfig(
        filename="logs_test.log",
        filemode='a',
        encoding='utf-8'
    )

    g_loger = logging.getLogger('global_logger')

    coloredlogs.install(
        fmt = "{name} | {asctime}:{msecs:.0f} | {message}",
        style="{",
        datefmt="%m/%d %H:%M:%S",
    )

    main()
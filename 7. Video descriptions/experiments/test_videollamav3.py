import os
import time
import shutil
import logging

import torch
from transformers import AutoModelForCausalLM, AutoProcessor

from params import Params

# Consts
DEVICE = "cuda:1"
MODEL_PATH = "DAMO-NLP-SG/VideoLLaMA3-7B"
ROOT = "/app/dataset/nintendo-snes-spc"
RES_FOLDER = "./results"

# Set of params
params = [
    Params(),
    Params(1, 1),
    Params(1, 20, "You will receive gameplays and should highlight useful features for creating a song."),
    Params(5),
    Params(5, 1),
    Params(5, 20, "You will receive gameplays and should highlight useful features for creating a song.")
]

# Videos
ALADIN = "aladdin/videos/aladdin_00169.mp4"
AIRCAV = "air-cavalry/videos/air-cavalry_00065.mp4"
BEETHOVEN = "beethoven-the-ultimate-canine-caper/videos/beethoven-the-ultimate-canine-caper_00061.mp4"
ALIEN_PREDATOR = "alien-vs-predator/videos/alien-vs-predator_00355.mp4" 
ALIEN_PREDATOR_MENU = "alien-vs-predator/videos/alien-vs-predator_00155.mp4" 
CAPCOM_SOCCER = "capcoms-soccer-shootout/videos/capcoms-soccer-shootout_00023.mp4"
CHRONO_DIALOG = "chrono-trigger/videos/chrono-trigger_01615.mp4"
DINOCITY = "dinocity/videos/dinocity_00193.mp4"
DKC3 = "donkey-kong-country-3-dixie-kongs-double-trouble/videos/donkey-kong-country-3-dixie-kongs-double-trouble_00199.mp4"
FZERO = "f-zero/videos/f-zero_00053.mp4"
SUPERR = "super-r-type/videos/super-r-type_00225.mp4"
SUPERMARIO = "super-mario-all-stars/videos/super-mario-all-stars_00127.mp4"
MARIOKART= "super-mario-kart/videos/super-mario-kart_00009.mp4"

experiment_videos = [ALADIN, AIRCAV, BEETHOVEN, ALIEN_PREDATOR, ALIEN_PREDATOR_MENU, CAPCOM_SOCCER, CHRONO_DIALOG, DINOCITY, DKC3, FZERO, SUPERR, SUPERMARIO, MARIOKART]

if not os.path.isdir(RES_FOLDER):
    os.mkdir(RES_FOLDER)

# Global log configs
logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime}:{msecs:.0f}, {message}", style="{",
    datefmt="%m-%d %H:%M:%S",
)

# global logger -> one csv with all the logs
CSV_HEADER = "video, fps, top_k, system prompt, generated text, execution time"
g_loger_path = os.path.join(RES_FOLDER, "logs.csv")
g_log_f = logging.FileHandler(g_loger_path, 'a', 'utf-8')
g_loger = logging.getLogger('global_logger')
g_loger.addHandler(g_log_f)

g_loger.debug(CSV_HEADER)

# Model
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True,
    device_map=DEVICE,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
)

# Loop all params and videos
for exp_vid in experiment_videos:
    # Paths
    original_video_path = os.path.join(ROOT, exp_vid)
    original_video_file_name = exp_vid.split('/')[-1]
    game_name = exp_vid.split('/')[0]
    
    video_result_folder = os.path.join(RES_FOLDER, game_name)
    cp_video_path = os.path.join(video_result_folder, original_video_file_name)
    log_path = os.path.join(video_result_folder, original_video_file_name[:-3]+"csv")

    if not os.path.isdir(video_result_folder):
        os.mkdir(video_result_folder)

    # Logger
    vid_logger = logging.getLogger(original_video_file_name)
    vid_log_f = logging.FileHandler(log_path, 'a', 'utf-8')
    vid_logger.addHandler(vid_log_f)
    vid_logger.debug(CSV_HEADER)

    # Copy video
    shutil.copyfile(original_video_path, cp_video_path)

    for param in params:
        start_time = time.process_time()

        conversation = [
            {"role": "system", "content": param.system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "video", "video": {"video_path":cp_video_path, "fps": param.fps}},
                    {"type": "text", "text": "What are the actions happening in the video?"},
                    {"type": "text", "text": "How does the game environment look like?"},
                    {"type": "text", "text": "Describe the game art style."},
                    {"type": "text", "text": "What is the movement speed in the video?"},
                    {"type": "text", "text": "What are the game mechanics and its genre?"},
                ]
            }
        ]

        processor = AutoProcessor.from_pretrained(MODEL_PATH, trust_remote_code=True)

        inputs = processor(
            conversation=conversation, #TODO batch???
            add_system_prompt=True,
            add_generation_prompt=True,
            return_tensors="pt"
        )

        inputs = {k: v.to(DEVICE) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}

        if "pixel_values" in inputs:
            inputs["pixel_values"] = inputs["pixel_values"].to(torch.bfloat16)

        output_ids = model.generate(**inputs, max_new_tokens=512, top_k=param.top_k)
        response = processor.batch_decode(output_ids, skip_special_tokens=True)[0].strip()

        elapsed_time = time.process_time() - start_time

        log_str = f'{original_video_file_name}, {param.fps}, {param.top_k}, {param.system_prompt}, "{response}", {elapsed_time}'
        g_loger.debug(log_str)
        vid_logger.debug(log_str)
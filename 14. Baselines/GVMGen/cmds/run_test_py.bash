#!/bin/bash

export AUDIOCRAFT_TEAM=default
export USER=felipe
export CUDA_VISIBLE_DEVICES=5

python3 /app/code/test.py --video_path /app/xps/mock/3-ninjas-kick-back_00091.mp4 --syn_path /app/xps/mock/ --fps 3 --duration 10
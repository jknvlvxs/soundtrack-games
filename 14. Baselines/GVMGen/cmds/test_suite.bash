#!/bin/bash

export AUDIOCRAFT_TEAM=default
export USER=felipe
export CUDA_VISIBLE_DEVICES=4

python3 /app/code/test_suite.py #--state_dict_bin_folder /app/code/checkpoints_tunado --model_name gvmgen_tuned
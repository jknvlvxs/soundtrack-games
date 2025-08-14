export CUDA_VISIBLE_DEVICES=2

python3 /app/code/compute_audio_embeddings.py

# nohup bash cmds/compute_audio_embeddings.bash > audio_embeddings.out &
export CUDA_VISIBLE_DEVICES=5

python3 /app/code/inference.py \
    --model-config /app/code/best_model.json \
    --ckpt-path /app/xps/sonique/original/ckpts/stable_ep=220.ckpt \
    --use-video true \
    --input-video /app/xps/mock/3-ninjas-kick-back_00091.mp4
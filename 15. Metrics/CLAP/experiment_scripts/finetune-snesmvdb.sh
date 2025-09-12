#!/bin/bash
#SBATCH --comment clap
#SBATCH --partition=g40423
#SBATCH --job-name=mclap
#SBATCH --nodes 3
#SBATCH --ntasks-per-node 8
#SBATCH --cpus-per-gpu=6
#SBATCH --exclusive
#SBATCH --output=%x_%j.out

# module load openmpi
# module load cuda/11.7
# export NCCL_PROTO=simple
# export FI_EFA_FORK_SAFE=1
# export FI_LOG_LEVEL=1
# export FI_EFA_USE_DEVICE_RDMA=1 # use for p4dn
# export NCCL_DEBUG=info
# export OMPI_MCA_mtl_base_verbose=1
# export FI_EFA_ENABLE_SHM_TRANSFER=0
# export FI_PROVIDER=efa
# export FI_EFA_TX_MIN_CREDITS=64
# export NCCL_TREE_THRESHOLD=0

# # sent to sub script
# export HOSTNAMES=`scontrol show hostnames "$SLURM_JOB_NODELIST"`
# export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
# export MASTER_PORT=12802
# export COUNT_NODE=`scontrol show hostnames "$SLURM_JOB_NODELIST" | wc -l`

# echo go $COUNT_NODE
# echo $HOSTNAMES

#source /fsx/yusong/clap/bin/activate
#cd /fsx/yusong/CLAP/src
export CUDA_VISIBLE_DEVICES=1
export TRANSFORMERS_CACHE=/app/xps/clap_transformers_cache

# We'll say it's not webdataset, so it will skip collecting the .tar files 
# I've modified the code so we don't need to set train_data and val_data by hand

#TODO: --freeze-text \
# --lp-loss="ce" \
# --lp-metrics="acc" \
#    --report-to "wandb" \

    # --data-truncating "fusion" \
    # --fusion-type "aff_2d" \
cd /app/code/src/laion_clap

# Should use the training script for fine tuning
# https://github.com/LAION-AI/CLAP/issues/141#issuecomment-2028780453

python -m training.main \
    --save-frequency 5 \
    --save-top-performance 3 \
    --save-most-recent \
    --dataset-type="mvdb_audiocraft" \
    --precision="fp32" \
    --warmup 0 \
    --batch-size=128 \
    --lr=1e-4 \
    --wd=0.1 \
    --epochs=15 \
    --workers=8 \
    --use-bn-sync \
    --amodel HTSAT-base \
    --tmodel roberta \
    --datasetnames "musicgen_snes_mvdb" \
    --datasetinfos "train" "eval" \
    --seed 3407 \
    --datasetpath /app/xps/ \
    --report-to "tensorboard" \
    --logs /app/xps/clap_logs \
    --gather-with-grad \
    --lp-lr=1e-4 \
    --lp-mlp \
    --openai-model-cache-dir /app/xps/clap_transformers_cache \
    --pretrained="/app/xps/clap/music_audioset_epoch_15_esc_90.14.pt" \
    --data-filling "repeatpad" \
    --data-truncating "rand_trunc" \
    --optimizer "adam"
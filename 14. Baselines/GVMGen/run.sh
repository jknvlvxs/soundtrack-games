export AUDIOCRAFT_TEAM=default
export USER=gvmgen # Will create an audiocraft_felipe folder inside checkpoints
export CUDA_VISIBLE_DEVICES=1

dora -P module run \
    solver=gvmgen/gvmgen \
    model/lm/model_scale=large \
    continue_from=/app/code/checkpoints/state_dict.bin \
    dataset.batch_size=4 \
    optim.updates_per_epoch=100 \
    dataset.valid.num_samples=10
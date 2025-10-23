export AUDIOCRAFT_TEAM=default
export USER=gvmgen # Will create an audiocraft_felipe folder inside checkpoints
export CUDA_VISIBLE_DEVICES=5

dora -P module run \
    solver=gvmgen/gvmgen \
    model/lm/model_scale=large \
    continue_from=/app/code/checkpoints/original/state_dict.bin \
    dataset.num_workers=2 \
    dataset.batch_size=2 \
    dataset.generate.num_samples=2 \
    dataset.valid.num_samples=2 \
    schedule.cosine.warmup=1 \
    optim.optimizer=adamw \
    optim.lr=1e-5 \
    optim.epochs=2 \
    optim.updates_per_epoch=2 \
    optim.adam.weight_decay=0.01 \
    deadlock.timeout=1200 \
    generate.lm.prompted_samples=False \
    generate.lm.unprompted_samples=True
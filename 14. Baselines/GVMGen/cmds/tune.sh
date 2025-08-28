export AUDIOCRAFT_TEAM=default
export USER=gvmgen # Will create an audiocraft_felipe folder inside checkpoints
export CUDA_VISIBLE_DEVICES=0

dora -P module run \
    solver=gvmgen/gvmgen \
    model/lm/model_scale=large \
    continue_from=/app/code/checkpoints/state_dict.bin \
    dataset.num_workers=6 \
    dataset.batch_size=6 \
    dataset.generate.num_samples=10 \
    schedule.cosine.warmup=8 \
    optim.optimizer=adamw \
    optim.lr=1e-5 \
    optim.epochs=100 \
    optim.updates_per_epoch=1000 \
    optim.adam.weight_decay=0.01 \
    dataset.valid.num_samples=10 \
    deadlock.timeout=1200 \
    generate.lm.prompted_samples=False \
    generate.lm.unprompted_samples=True
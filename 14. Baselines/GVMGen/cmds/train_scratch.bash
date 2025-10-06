export AUDIOCRAFT_TEAM=default
export USER=gvmgen # Will create an audiocraft_felipe folder inside checkpoints
export CUDA_VISIBLE_DEVICES=5

dora -P module run \
    solver=gvmgen/gvmgen \
    model/lm/model_scale=large \
    dataset.num_workers=6 \
    dataset.batch_size=6 \
    dataset.train.shuffle=true \
    dataset.train.disable_sampling=true \
    dataset.generate.num_samples=10 \
    dataset.valid.num_samples=500 \
    schedule.cosine.warmup=8 \
    optim.optimizer=adamw \
    optim.lr=1e-5 \
    optim.epochs=150 \
    optim.updates_per_epoch=null \
    optim.adam.weight_decay=0.01 \
    deadlock.timeout=1200 \
    generate.lm.prompted_samples=False \
    generate.lm.unprompted_samples=True
export AUDIOCRAFT_TEAM=default
export USER=gvmgen # Will create an audiocraft_felipe folder inside checkpoints
export CUDA_VISIBLE_DEVICES=4

# FAD
export CONDA_ENV_DIR="$CONDA_PREFIX/envs"
export TF_PYTHON_EXE="$CONDA_ENV_DIR/fad/bin/python"
export TF_LIBRARY_PATH="$CONDA_ENV_DIR/fad/lib/python3.10/site-packages/nvidia/cudnn/lib"

# By default dataset.evaluate.disable_sampling=true
dora -P module run \
    solver=gvmgen/gvmgen \
    model/lm/model_scale=large \
    continue_from=/app/code/checkpoints/original/state_dict.bin \
    dataset.num_workers=4 \
    dataset.batch_size=16 \
    +dataset.evaluate.batch_size=16 \
    +metrics.fad.tf.batch_size=16 \
    execute_only=evaluate \
    dataset.evaluate.disable_sampling=true \
    evaluate.metrics.fad=true \
    metrics.fad.tf.bin=/app/xps/fad/google-research \
    evaluate.metrics.kld=true \
    metrics.kld.use_gt=false \
    metrics.kld.passt.pretrained_length=30 \
    evaluate.metrics.genre_kld=true \
    metrics.genre_kld.use_gt=false \
    metrics.genre_kld.checkpoints=/app/xps/genre_classifier_new \
    evaluate.metrics.genre_class_metrics=true \
    metrics.genre_class_metrics.use_gt=false \
    metrics.genre_class_metrics.checkpoints=/app/xps/genre_classifier_new \
    evaluate.metrics.text_consistency=true \
    evaluate.metrics.gt_text_consistency=false \
    evaluate.metrics.tuned_text_consistency=true \
    evaluate.metrics.gt_tuned_text_consistency=false
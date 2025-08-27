export AUDIOCRAFT_TEAM=default
export USER=gvmgen # Will create an audiocraft_felipe folder inside checkpoints
export CUDA_VISIBLE_DEVICES=4

# dora -P module run \
#     solver=gvmgen/gvmgen \
#     model/lm/model_scale=large \
#     continue_from=/app/code/checkpoints/state_dict.bin \
#     dataset.num_workers=4 \
#     dataset.batch_size=4 \
#     +dataset.evaluate.batch_size=16 \
#     +metrics.fad.tf.batch_size=16 \
#     execute_only=evaluate \
#     dataset.evaluate.disable_sampling=true \ #TODO
#     evaluate.metrics.fad=false \
#     metrics.fad.tf.bin=/app/xps/fad/google-research \
#     evaluate.metrics.kld=true \
#     metrics.kld.passt.pretrained_length=30 \
#     evaluate.metrics.genre_kld=false \ #TODO?
#     metrics.genre_kld.checkpoints=/app/xps/genre_classifier \ #TODO?
#     evaluate.metrics.text_consistency=false #TODO

dora -P module run \
    solver=gvmgen/gvmgen \
    model/lm/model_scale=large \
    continue_from=/app/code/checkpoints/state_dict.bin \
    dataset.num_workers=4 \
    dataset.batch_size=4 \
    +dataset.evaluate.batch_size=16 \
    +metrics.fad.tf.batch_size=16 \
    execute_only=evaluate \
    evaluate.metrics.fad=false \
    metrics.fad.tf.bin=/app/xps/fad/google-research \
    evaluate.metrics.kld=false \
    metrics.kld.passt.pretrained_length=30 \
    evaluate.metrics.text_consistency=true
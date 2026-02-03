export LOCAL_MACHINE="felipe@10.255.0.107:/home/felipe/Desktop/state_dict/"
export XPS_FOLDER="/app/xps/audiocraft_gvmgen/xps/78439aeb_tuned_new_split"
export CHECKPOINTS_AND_INFERENCE_FODLER="../checkpoints"

#rsync -avzhP --exclude='*.th' $XPS_FOLDER $LOCAL_MACHINE
#rsync -avzhP $XPS_FOLDER $LOCAL_MACHINE

echo $CHECKPOINTS_AND_INFERENCE_FODLER
echo $LOCAL_MACHINE
rsync -avzhP $LOCAL_MACHINE $CHECKPOINTS_AND_INFERENCE_FODLER
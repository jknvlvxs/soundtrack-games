export LOCAL_MACHINE="felipe@10.255.0.107:/media/felipe/32740855-6a5b-4166-b047-c8177bb37be1/state_dict_bin_and_demo_inference/"
export XPS_FOLDER="/home/es119256/dados/xps/checkpoints_and_inference_final/"

#rsync -avzhP --exclude='*.th' $XPS_FOLDER $LOCAL_MACHINE
#rsync -avzhP $XPS_FOLDER $LOCAL_MACHINE

echo $XPS_FOLDER
echo $LOCAL_MACHINE
rsync -avzhP $XPS_FOLDER $LOCAL_MACHINE
export LOCAL_MACHINE="felipe@10.255.0.15:/home/felipe/Desktop/sonique/"
export CKPT_FOLDER="/home/es119256/vmdb/14. Baselines/sonique/ckpts/"

echo $LOCAL_MACHINE
echo $CKPT_FOLDER

rsync -avzhP $LOCAL_MACHINE "/home/es119256/vmdb/14. Baselines/sonique/ckpts/"
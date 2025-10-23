export FILE_ID=1kRy-B82ZGvRrJq4M5ob45jOvQgp9r_Xz
export FILE_NAME=ckpt.zip

wget --no-check-certificate \
     "https://drive.usercontent.google.com/download?id=${FILE_ID}&confirm=t" \
     -O "${FILE_NAME}"
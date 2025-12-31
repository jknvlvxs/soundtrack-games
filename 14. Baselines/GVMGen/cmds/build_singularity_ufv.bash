#!/bin/bash

# set -e
# set -u
# set -o pipefail
set -x

# Carregar módulos necessários
module --force purge
module load GCCcore/12.2.0 
module load CUDA/12.6.0
module load Apptainer/1.2.2

# singularity cache clean --force

# /tmp & /cache to a partition with space
export APPTAINER_TMPDIR="/home/es119256/dados/my_temp"
export APPTAINER_CACHEDIR="/home/es119256/dados/my_cache"
export APPTAINER_SQUASHFS_OPTS="-comp gzip -b 1048576"

mkdir -p $APPTAINER_TMPDIR
mkdir -p $APPTAINER_CACHEDIR

# Build as sandbox -> worked
singularity build --sandbox containers/gvmgen_singularity/ containers/gvmgen_singularity.def
# Convert to sif
#TODO: Not working
# singularity build containers/gvmgen_singularity.sif containers/gvmgen_singularity/
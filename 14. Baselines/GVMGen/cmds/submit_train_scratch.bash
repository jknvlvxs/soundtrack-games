#!/bin/bash
#SBATCH --job-name=tune_gvmgen          # Nome do job
#SBATCH --mail-type=ALL                 # Opções: BEGIN, END, FAIL, ALL, etc.
#SBATCH --mail-user=felipeferreiramarra@gmail.com       # Endereço de e-mail destinatário
#SBATCH --partition=scientific          # Partição
#SBATCH --qos=scientific-qos            # QoS 
#SBATCH --nodes=1                       # Número de nós 1 de 1
#SBATCH --ntasks=1                      # Número de tarefas
#SBATCH --cpus-per-task=32               # CPUs por tarefa 8 de 128 (Max)
#SBATCH --mem=512G                       # Memória RAM 32GB de 1007GB(Max)
#SBATCH --gres=gpu:1               # Solicitar 1 GPU de 4 (Max)
#SBATCH --time=2-00:00:00               # Tempo máximo (2 dias)
#SBATCH --output=job_%j.out        # Arquivo de saída (%j = job ID)
#SBATCH --error=job_%j.err         # Arquivo de erro

# Carregar módulos necessários
module --force purge
module load GCCcore/12.2.0 
module load CUDA/12.6.0
module load Apptainer/1.2.2

# Informações do job
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_NODELIST"
echo "GPUs alocadas: $CUDA_VISIBLE_DEVICES"
echo "Memória disponível: $(free -h | grep Mem:)"
echo "Limites do processo:"
ulimit -a | egrep 'virtual memory|max resident set|open files'
echo "Iniciado em: $(date)"

# Bind host folder to the container. In this way I'm only working on the host files
# The container will be just like an isoladed env to run the code
export APPTAINER_BIND="/home/es119256/dados/repos/vmdb/14. Baselines/GVMGen:/app/code,/home/es119256/dados/xps:/app/xps,/home/es119256/dados/datasets/vmdb_3:/app/dataset"

# singularity exec --cleanenv --nv "/home/es119256/dados/repos/vmdb/14. Baselines/GVMGen/containers/gvmgen_singularity" \
#     bash -c """
# set -x
# set -e

# python3 -u /app/code/data_preprocess/snesmvdb_to_gvmgen.py
# """

singularity exec --nv "/home/es119256/dados/repos/vmdb/14. Baselines/GVMGen/containers/gvmgen_singularity" \
    bash -c """
export AUDIOCRAFT_TEAM=default
export USER=gvmgen

export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

cd /app/code

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
"""

echo "Memória final: $(free -h | grep Mem:)"
echo "Finalizado em: $(date)"
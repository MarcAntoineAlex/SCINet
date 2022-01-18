#!/bin/bash
#SBATCH --partition=dell
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:V100:2
#SBATCH -J scinet
#SBATCH -o log/job-%j.log
#SBATCH -e log/job-%j.err
# shellcheck disable=SC2046
# shellcheck disable=SC2006
echo Time is `date`
echo Directory is $PWD
echo This job runs on the following nodes:
echo "$SLURM_JOB_NODELIST"
cd ..
eval "$(conda shell.bash hook)"
source /home/LAB/anaconda3/bin/activate base
# conda --version
# which python
conda activate gch
echo Python:
which python
export NCCL_IB_DISABLE=1
# export NCCL_DEBUG=INFO
# export NCCL_DEBUG_SUBSYS=ALL
export MKL_THREADING_LAYER=GNU
export CUDA_HOME=/usr/local/cuda-10.2
# sugon does not support infiniband
srun python run_ETTh.py --data ETTh1 --features M  --seq_len 48 --label_len 24 --pred_len 24 --hidden-size 4 --stacks 1 --levels 3 --lr 3e-3 --batch_size 8 --dropout 0.5 --model_name etth1_M_I48_O24_lr3e-3_bs8_dp0.5_h4_s1l3
srun python run_ETTh.py --data ETTh1 --features M  --seq_len 96 --label_len 48 --pred_len 48 --hidden-size 4 --stacks 1 --levels 3 --lr 0.009 --batch_size 16 --dropout 0.25 --model_name etth1_M_I96_O48_lr0.009_bs16_dp0.25_h4_s1l3
srun python run_ETTh.py --data ETTh1 --features M  --seq_len 336 --label_len 168 --pred_len 168 --hidden-size 4 --stacks 1 --levels 3 --lr 5e-4 --batch_size 32 --dropout 0.5 --model_name etth1_M_I336_O168_lr5e-4_bs32_dp0.5_h4_s1l3
srun python run_ETTh.py --data ETTh1 --features M  --seq_len 336 --label_len 336 --pred_len 336 --hidden-size 1 --stacks 1 --levels 4 --lr 1e-4 --batch_size 512 --dropout 0.5 --model_name etth1_M_I336_O336_lr1e-4_bs512_dp0.5_h1_s1l4
srun python run_ETTh.py --data ETTh1 --features M  --seq_len 736 --label_len 720 --pred_len 720 --hidden-size 1 --stacks 1 --levels 5 --lr 5e-5 --batch_size 256 --dropout 0.5 --model_name etth1_M_I736_O720_lr5e-5_bs256_dp0.5_h1_s1l5

srun python run_ETTh.py --data ETTh1 --features M  --seq_len 96 --label_len 48 --pred_len 24 --hidden-size 4 --stacks 1 --levels 3 --lr 3e-3 --batch_size 8 --dropout 0.5 --model_name etth1_M_I48_O24_lr3e-3_bs8_dp0.5_h4_s1l3_
srun python run_ETTh.py --data ETTh1 --features M  --seq_len 96 --label_len 48 --pred_len 48 --hidden-size 4 --stacks 1 --levels 3 --lr 0.009 --batch_size 16 --dropout 0.25 --model_name etth1_M_I96_O48_lr0.009_bs16_dp0.25_h4_s1l3_
srun python run_ETTh.py --data ETTh1 --features M  --seq_len 96 --label_len 48 --pred_len 168 --hidden-size 4 --stacks 1 --levels 3 --lr 5e-4 --batch_size 32 --dropout 0.5 --model_name etth1_M_I336_O168_lr5e-4_bs32_dp0.5_h4_s1l3_
srun python run_ETTh.py --data ETTh1 --features M  --seq_len 96 --label_len 48 --pred_len 336 --hidden-size 1 --stacks 1 --levels 4 --lr 1e-4 --batch_size 512 --dropout 0.5 --model_name etth1_M_I336_O336_lr1e-4_bs512_dp0.5_h1_s1l4_
srun python run_ETTh.py --data ETTh1 --features M  --seq_len 96 --label_len 48 --pred_len 720 --hidden-size 1 --stacks 1 --levels 5 --lr 5e-5 --batch_size 256 --dropout 0.5 --model_name etth1_M_I736_O720_lr5e-5_bs256_dp0.5_h1_s1l5_

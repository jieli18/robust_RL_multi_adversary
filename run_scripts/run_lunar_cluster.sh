#!/bin/bash

#############################################################################################
####################              4/19
#############################################################################################
# 10 ADV RARL lunar lander w/o memory
#ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
#--num_iters 1000 --train_batch_size 10000 --checkpoint_freq 100 --num_concat_states 1 \
#--num_adv_strengths 1 --advs_per_strength 10 --advs_per_rew 1 --num_adv_rews 10 --grid_search --use_s3 \
#--exp_title lunar_RARL_10adv_concat1_grid_r4 --num_cpus 9 --run_transfer_tests --multi_node \
#--adv_strength 0.25 --adv_all_actions --algorithm PPO" \
#--start --stop --tmux --cluster-name=ev_lun_test3
#
## 10 ADV DMALT lunar lander w/o memory
#ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
#--num_iters 1000 --train_batch_size 10000 --checkpoint_freq 100 --num_concat_states 1 \
#--num_adv_strengths 1 --advs_per_strength 10 --advs_per_rew 1 --num_adv_rews 10 --grid_search --use_s3 \
#--exp_title lunar_DMALT_10adv_concat1_grid_r4 --num_cpus 9 --run_transfer_tests --multi_node \
#--adv_strength 0.25 --adv_all_actions --reward_range --low_reward -200 --high_reward 300 --algorithm PPO" \
#--start --stop --tmux --cluster-name=ev_lun_test4
#
## Domain randomization baseline
#ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
#--num_iters 1000 --checkpoint_freq 100 --num_concat_states 1 \
#--num_adv_strengths 0 --advs_per_strength 0 --advs_per_rew 9 --num_adv_rews 0 --grid_search --use_s3 \
#--exp_title lunar_dr_concat1_grid_r4 --num_cpus 1 --run_transfer_tests --multi_node --domain_randomization --algorithm PPO" \
#--start --stop --tmux --cluster-name=ev_lun_test5
#
#ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
#--num_iters 1000 --train_batch_size 10000 --timesteps_total 1000000 --checkpoint_freq 100 --num_concat_states 1 \
#--num_adv_strengths 1 --advs_per_strength 10 --advs_per_rew 1 --num_adv_rews 10 --grid_search --use_s3 \
#--exp_title lunar_RARL_10adv_concat1_grid_r6 --num_cpus 9 --run_transfer_tests --multi_node \
#--adv_strength 0.25 --adv_all_actions --algorithm PPO" \
#--start --stop --tmux --cluster-name=ev_lun_test6
#
## 10 ADV DMALT lunar lander w/o memory
#ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
#--num_iters 1000 --train_batch_size 10000 --timesteps_total 1000000 --checkpoint_freq 100 --num_concat_states 1 \
#--num_adv_strengths 1 --advs_per_strength 10 --advs_per_rew 1 --num_adv_rews 10 --grid_search --use_s3 \
#--exp_title lunar_DMALT_10adv_concat1_grid_r6 --num_cpus 9 --run_transfer_tests --multi_node \
#--adv_strength 0.25 --adv_all_actions --reward_range --low_reward 100 --high_reward 300 --algorithm PPO" \
#--start --stop --tmux --cluster-name=ev_lun_test7
#
## Domain randomization baseline
#ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
#--num_iters 1000 --checkpoint_freq 100 --timesteps_total 1000000 --num_concat_states 1 \
#--num_adv_strengths 0 --advs_per_strength 0 --advs_per_rew 9 --num_adv_rews 0 --grid_search --use_s3 \
#--exp_title lunar_dr_concat1_grid_r6 --num_cpus 1 --run_transfer_tests --multi_node --domain_randomization --algorithm PPO" \
#--start --stop --tmux --cluster-name=ev_lun_test8


#############################################################################################
####################              5/18
#############################################################################################
#ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
#--num_iters 1000 --train_batch_size 10000 --timesteps_total 1000000 --checkpoint_freq 100 --num_concat_states 1 \
#--num_adv_strengths 1 --advs_per_strength 1 --advs_per_rew 1 --num_adv_rews 1 --grid_search --use_s3 \
#--exp_title lunar_RARL_1adv_concat1_grid_r6 --num_cpus 9 --run_transfer_tests --multi_node \
#--adv_strength 0.25 --adv_all_actions --algorithm PPO" \
#--start --stop --tmux --cluster-name=ev_lun_test6

##############################################################################################
#####################              5/30. GRID SEARCH.
##############################################################################################
#
## DR Baseline
#ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
#--num_iters 1000 --checkpoint_freq 100 --timesteps_total 1000000 --num_concat_states 1 \
#--num_adv_strengths 0 --advs_per_strength 0 --advs_per_rew 9 --num_adv_rews 0 --grid_search --use_s3 \
#--exp_title lunar_dr_concat1_grid_r6 --num_cpus 2 --run_transfer_tests --multi_node --domain_randomization --algorithm PPO" \
#--start --stop --tmux --cluster-name=ev_lun_test1
#
## 1 ADV RARL lunar lander w/o memory
#ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
#--num_iters 1000 --train_batch_size 10000 --checkpoint_freq 100 --num_concat_states 1 \
#--num_adv_strengths 1 --advs_per_strength 1 --advs_per_rew 1 --num_adv_rews 1 --grid_search --use_s3 \
#--exp_title lunar_RARL_1adv_concat1_grid --num_cpus 2 --run_transfer_tests --multi_node \
#--adv_all_actions --algorithm PPO" \
#--start --stop --tmux --cluster-name=ev_lun_test2
#
## 3 ADV RARL lunar lander w/o memory
#ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
#--num_iters 1000 --train_batch_size 10000 --checkpoint_freq 100 --num_concat_states 1 \
#--num_adv_strengths 1 --advs_per_strength 3 --advs_per_rew 3 --num_adv_rews 1 --grid_search --use_s3 \
#--exp_title lunar_RARL_3adv_concat1_grid --num_cpus 2 --run_transfer_tests --multi_node \
#--adv_all_actions --algorithm PPO" \
#--start --stop --tmux --cluster-name=ev_lun_test3
#
## 5 ADV RARL lunar lander w/o memory
#ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
#--num_iters 1000 --train_batch_size 10000 --checkpoint_freq 100 --num_concat_states 1 \
#--num_adv_strengths 1 --advs_per_strength 5 --advs_per_rew 5 --num_adv_rews 1 --grid_search --use_s3 \
#--exp_title lunar_RARL_5adv_concat1_grid --num_cpus 2 --run_transfer_tests --multi_node \
#--adv_all_actions --algorithm PPO" \
#--start --stop --tmux --cluster-name=ev_lun_test4

#############################################################################################
####################              5/30. SEED SEARCH.
#############################################################################################

# DR Baseline
ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
--num_iters 1000 --checkpoint_freq 100 --timesteps_total 1000000 --num_concat_states 1 \
--num_adv_strengths 0 --advs_per_strength 0 --advs_per_rew 9 --num_adv_rews 0 --seed_search --use_s3 \
--exp_title lunar_dr_concat1_seed_lrp0005_lv0p9 --num_cpus 2 --run_transfer_tests --multi_node --domain_randomization
--algorithm PPO --lr 0.0005 --lambda_val 0.9" \
--start --stop --tmux --cluster-name=ev_lun_test1

# 1 ADV RARL lunar lander w/o memory
ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
--num_iters 1000 --train_batch_size 10000 --checkpoint_freq 100 --num_concat_states 1 \
--num_adv_strengths 1 --advs_per_strength 1 --advs_per_rew 1 --num_adv_rews 1 --seed_search --use_s3 \
--exp_title lunar_RARL_1adv_concat1_seed_lrp0005_lv0p9 --num_cpus 2 --run_transfer_tests --multi_node \
--adv_all_actions --algorithm PPO --lr 0.0005 --lambda_val 0.9" \
--start --stop --tmux --cluster-name=ev_lun_test2

# 3 ADV RARL lunar lander w/o memory
ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
--num_iters 1000 --train_batch_size 10000 --checkpoint_freq 100 --num_concat_states 1 \
--num_adv_strengths 1 --advs_per_strength 3 --advs_per_rew 3 --num_adv_rews 1 --seed_search --use_s3 \
--exp_title lunar_RARL_3adv_concat1_seed_lrp0005_lv1p0 --num_cpus 2 --run_transfer_tests --multi_node \
--adv_all_actions --algorithm PPO --lr 0.0005 --lambda_val 1.0" \
--start --stop --tmux --cluster-name=ev_lun_test3

# 5 ADV RARL lunar lander w/o memory
ray exec ../autoscale.yaml "python /home/ubuntu/adversarial_sim2real/run_scripts/lunar_lander/run_lunar_lander.py \
--num_iters 1000 --train_batch_size 10000 --checkpoint_freq 100 --num_concat_states 1 \
--num_adv_strengths 1 --advs_per_strength 5 --advs_per_rew 5 --num_adv_rews 1 --seed_search --use_s3 \
--exp_title lunar_RARL_5adv_concat1_seed_lrp0005_lv1p0 --num_cpus 2 --run_transfer_tests --multi_node \
--adv_all_actions --algorithm PPO --lr 0.0005 --lambda_val 1.0" \
--start --stop --tmux --cluster-name=ev_lun_test5
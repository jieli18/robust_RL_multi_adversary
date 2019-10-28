import argparse
import configparser
from datetime import datetime
import os
import sys

import ray
import ray.rllib.agents.ppo as ppo
from ray.rllib.models import ModelCatalog
from ray.tune import run as run_tune
from ray.tune import grid_search
from ray.tune.registry import register_env

from envs.crowd_env import CrowdSimEnv
from envs.policy.policy_factory import policy_factory
from envs.utils.robot import Robot
from utils.parsers import init_parser, env_parser, ray_parser

from ray.rllib.models.catalog import MODEL_DEFAULTS
from models.models import ConvLSTM


def setup_exps(args):
    parser = init_parser()
    parser = env_parser(parser)
    parser = ray_parser(parser)
    args = parser.parse_args(args)

    alg_run = 'PPO'
    config = ppo.DEFAULT_CONFIG.copy()
    config['num_workers'] = args.num_cpus
    config['gamma'] = tune.grid_search([0.5, 0.9, 0.99, 0.999])
    config['lr'] = 5e-5
    config['train_batch_size'] = 10000
    config['vf_loss_coeff'] = 1e-2

    config['env_config']['run'] = alg_run
    config['env_config']['policy'] = args.policy
    config['env_config']['show_images'] = args.show_images
    config['env_config']['train_on_images'] = args.train_on_images

    with open(args.env_params, 'r') as file:
        env_params = file.read()

    with open(args.policy_params, 'r') as file:
        policy_params = file.read()

    config['env_config']['env_params'] = env_params
    config['env_config']['policy_params'] = policy_params

    # pick out the right model
    if args.train_on_images:
        # register the custom model
        ModelCatalog.register_custom_model("rnn", ConvLSTM)

        conv_filters = [
            [32, [3, 3], 2],
            [32, [3, 3], 2],
        ]
        config['model'] = MODEL_DEFAULTS.copy()
        
        config['model']['conv_activation'] = 'relu'
        config['model']['use_lstm'] = True
        config['model']['lstm_use_prev_action_reward'] = True
        config['model']['lstm_cell_size'] = 128
        config['model']['custom_options']['fcnet_hiddens'] = [[32, 32], []]
        config['model']['conv_filters'] = conv_filters
        config['model']['custom_model'] = "rnn"
        
        config['vf_share_layers'] = True
    else:
        config['model'] = {'use_lstm': True, "lstm_use_prev_action_reward": True, 'lstm_cell_size': 128}
        config['vf_share_layers'] = True
        config['vf_loss_coeff'] = 1e-4

    s3_string = 's3://sim2real/' \
                + datetime.now().strftime('%m-%d-%Y') + '/' + args.exp_title
    config['env'] = 'CrowdSim'
    register_env('CrowdSim', env_creator)

    exp_dict = {
        'name': args.exp_title,
        'run_or_experiment': alg_run,
        'checkpoint_freq': args.checkpoint_freq,
        'stop': {
            'training_iteration': args.num_iters
        },
        'config': config,
        'num_samples': args.num_samples,
    }
    if args.use_s3:
        exp_dict['upload_dir'] = s3_string

    return exp_dict, args


def env_creator(passed_config):
    config_path = passed_config['env_params']
    
    env_params = configparser.RawConfigParser()
    env_params.read_string(config_path)
    
    robot = Robot(env_params, 'robot')
    env = CrowdSimEnv(env_params, robot)

    # additional configuration
    env.show_images = passed_config['show_images']
    env.train_on_images = passed_config['train_on_images']

    # configure policy
    policy_params = configparser.RawConfigParser()
    policy_params.read_string(passed_config['policy_params'])
    policy = policy_factory[passed_config['policy']](policy_params)
    if not policy.trainable:
        sys.exit('Policy has to be trainable')
    if passed_config['policy_params'] is None:
        sys.exit('Policy config has to be specified for a trainable network')

    robot.set_policy(policy)
    policy.set_env(env)
    robot.print_info()
    return env

if __name__=="__main__":

    exp_dict, args = setup_exps(sys.argv[1:])
    
    if args.multi_node:
        ray.init(redis_address='localhost:6379')
    else:
        ray.init()

    run_tune(**exp_dict, queue_trials=False)


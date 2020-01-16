import errno
from datetime import datetime
from functools import reduce
import random
import os
import subprocess
import sys

import pytz
import numpy as np
import ray
from ray.rllib.agents.ppo.ppo_policy import PPOTFPolicy
from ray.rllib.agents.ppo.ppo import PPOTrainer, DEFAULT_CONFIG

from ray.rllib.models import ModelCatalog
from ray import tune
from ray.tune import run as run_tune
from ray.tune.registry import register_env

# from algorithms.custom_ppo import KLPPOTrainer, CustomPPOPolicy, DEFAULT_CONFIG

from visualize.pendulum.transfer_tests import run_transfer_tests
from visualize.pendulum.model_adversary_grid import visualize_model_perf
from visualize.pendulum.visualize_adversaries import visualize_adversaries
from utils.parsers import init_parser, ray_parser, ma_env_parser
from utils.pendulum_env_creator import pendulum_env_creator
from utils.rllib_utils import get_config_from_path

from models.recurrent_tf_model_v2 import LSTM


def setup_ma_config(config):
    env = pendulum_env_creator(config['env_config'])

    num_adversaries = config['env_config']['num_adversaries']

    if num_adversaries > 0 and not config['env_config']['model_based']:
        policies_to_train = ['pendulum']
        policy_graphs = {'pendulum': (PPOTFPolicy, env.observation_space, env.action_space, {})}
        adv_policies = ['adversary' + str(i) for i in range(num_adversaries)]
        adversary_config = {"model": {'fcnet_hiddens': [32, 32], 'use_lstm': False, 'custom_model': {}}}
        policy_graphs.update({adv_policies[i]: (PPOTFPolicy, env.adv_observation_space,
                                                env.adv_action_space, adversary_config) for i in range(num_adversaries)})
    # TODO(@evinitsky) put this back
    # policy_graphs.update({adv_policies[i]: (CustomPPOPolicy, env.adv_observation_space,
    #                                         env.adv_action_space, adversary_config) for i in range(num_adversaries)})

        policies_to_train += adv_policies
    else:
        return

    def policy_mapping_fn(agent_id):
        return agent_id

    config.update({
        'multiagent': {
            'policies': policy_graphs,
            'policy_mapping_fn': policy_mapping_fn,
            'policies_to_train': policies_to_train
        }
    })


def setup_exps(args):
    parser = init_parser()
    parser = ray_parser(parser)
    parser = ma_env_parser(parser)
    parser.add_argument('--custom_ppo', action='store_true', default=False, help='If true, we use the PPO with a KL penalty')
    parser.add_argument('--use_lstm', action='store_true', default=False, help='If true, the custom LSTM is turned on')
    parser.add_argument('--num_adv', type=int, default=5, help='Number of active adversaries in the env')
    parser.add_argument('--adv_strength', type=float, default=0.1, help='Strength of active adversaries in the env')
    parser.add_argument('--model_based', action='store_true', default=False,
                        help='If true, the adversaries are a set of fixed sinusoids instead of being learnt')
    parser.add_argument('--guess_adv', action='store_true', default=False,
                        help='If true, a prediction head is added that the agent uses to guess '
                             'which adversary is currently active')
    parser.add_argument('--guess_next_state', action='store_true', default=False,
                        help='If true, a prediction head is added that the agent uses to guess '
                             'what the next state is going to be')
    parser.add_argument('--num_concat_states', type=int, default=1,
                        help='Set the number of states that we will concatenate together')
    parser.add_argument('--adversary_type', type=str, default='cos',
                        help='Set which type of adversary is active. Options are --sin and --state_func'
                             'and --rand_state_func'
                             '--cos sets sine waves as the active adversaries'
                             '--state_func initializes random vectors that are a function of state'
                             '--rand_state_func samples a new random state vector at every rollout'
                             '--friction yields perturbations of the form [0, 0, -1] * scale_factor'
                             '--rand_friction yields similar perturbations are friction but resampled every rollout')
    parser.add_argument('--horizon', type=int, default=200)
    parser.add_argument('--big_grid_search', action='store_true', default=False,
                        help='If true, do a really big grid search')
    args = parser.parse_args(args)

    alg_run = 'PPO'

    # Universal hyperparams
    config = DEFAULT_CONFIG
    config['gamma'] = 0.995
    config["batch_mode"] = "complete_episodes"
    config['train_batch_size'] = args.train_batch_size
    config['vf_clip_param'] = 100.0
    config['lambda'] = 0.1
    if args.grid_search:
        config['lr'] = tune.grid_search([5e-4, 5e-5])
    elif args.big_grid_search:
        config['lr'] = tune.grid_search([1e-3, 5e-3, 5e-4])
        config['lambda'] = tune.grid_search([0.1, 0.5, 0.9])
    else:
        config['lr'] = 5e-4
    config['sgd_minibatch_size'] = min(500, args.train_batch_size)
    # config['num_envs_per_worker'] = 10
    config['num_sgd_iter'] = 10
    config['num_workers'] = args.num_cpus

    if args.custom_ppo:
        config['num_adversaries'] = args.num_adv
        config['kl_diff_weight'] = args.kl_diff_weight
        config['kl_diff_target'] = args.kl_diff_target
        config['kl_diff_clip'] = 5.0

    # Options used in every env
    config['env_config']['horizon'] = args.horizon
    config['env_config']['num_adversaries'] = args.num_adv
    config['env_config']['adversary_strength'] = args.adv_strength
    config['env_config']['model_based'] = args.model_based
    # These next options are only used in the model based env
    config['env_config']['guess_adv'] = args.guess_adv
    config['env_config']['guess_next_state'] = args.guess_next_state
    config['env_config']['num_concat_states'] = args.num_concat_states
    config['env_config']['adversary_type'] = args.adversary_type
    # These are some very specific flags
    if args.adversary_type == 'state_func':
        config['env_config']['weights'] = [np.random.uniform(low=-1, high=1, size=3)
                             for _ in range(args.num_adv)]
    elif args.adversary_type == 'friction':
        base_vector = np.array([0, 0, -1])
        scale_factors = np.linspace(start=0, stop=1, num=args.num_adv)
        state_weights = []
        for scale_factor in scale_factors:
            state_weights.append(base_vector * scale_factor)
        config['env_config']['weights'] = state_weights

    config['env_config']['run'] = alg_run

    if args.use_lstm:
        config['model']['fcnet_hiddens'] = [64, 64]
    else:
        config['model']['fcnet_hiddens'] = [256, 256, 256]
    if args.use_lstm:
        # ModelCatalog.register_custom_model("rnn", LSTM)
        # config['model']['custom_model'] = "rnn"
        # config['model']['custom_options'] = {'lstm_use_prev_action': True}
        config['vf_share_layers'] = True
        config['model']['lstm_cell_size'] = 128
        config['model']['use_lstm'] = True
        if args.grid_search:
            config['model']['max_seq_len'] = tune.grid_search([20, 40])
        # we aren't sweeping over this due to limited CPU numbers
        elif args.big_grid_search:
            config['model']['max_seq_len'] = 20

    if args.grid_search:
        if args.horizon > 200:
            config['vf_loss_coeff'] = tune.grid_search([1e-5, 1e-6])
        else:
            config['vf_loss_coeff'] = tune.grid_search([1e-4, 1e-3])
    elif args.big_grid_search:
        config['vf_loss_coeff'] = tune.grid_search([1e-5, 1e-6, 1e-7])

    else:
        config['vf_loss_coeff'] = 1e-5

    config['env'] = 'MAPendulumEnv'
    register_env('MAPendulumEnv', pendulum_env_creator)

    setup_ma_config(config)

    # add the callbacks
    config["callbacks"] = {"on_train_result": on_train_result,
                           "on_episode_end": on_episode_end}

    if args.model_based:
        config["callbacks"].update({"on_episode_step": on_episode_step,
                                    "on_episode_start": on_episode_start})

    # config["eager_tracing"] = True
    # config["eager"] = True
    # config["eager_tracing"] = True

    # create a custom string that makes looking at the experiment names easier
    def trial_str_creator(trial):
        return "{}_{}".format(trial.trainable_name, trial.experiment_tag)

    exp_dict = {
        'name': args.exp_title,
        # 'run_or_experiment': KLPPOTrainer,
        'run_or_experiment': 'PPO',
        'trial_name_creator': trial_str_creator,
        'checkpoint_freq': args.checkpoint_freq,
        'stop': {
            'training_iteration': args.num_iters
        },
        'config': config,
        'num_samples': args.num_samples,
    }
    return exp_dict, args


def on_episode_start(info):
    episode = info["episode"]
    episode.user_data["true_rew"] = []


def on_episode_step(info):
    episode = info["episode"]
    if hasattr(info["env"], 'envs'):
        env = info["env"].envs[0]
        episode.user_data["true_rew"].append(env.true_rew)

    elif hasattr(info["env"], 'vector_env'):
        envs = info["env"].vector_env.envs
        if hasattr(envs[0], 'true_rew'):
            true_rews = [env.true_rew for env in envs]
            # some of the envs won't actually be used if we are vectorizing so lets just ignore them
            rew_list = [true_rew for env, true_rew in zip(envs, true_rews) if env.step_num != 0]
            if len(rew_list) > 0:
                episode.user_data["true_rew"].append(np.mean(rew_list))


def on_train_result(info):
    """Store the mean score of the episode without the auxiliary rewards"""
    result = info["result"]
    # pendulum_reward = result['policy_reward_mean']['pendulum']
    trainer = info["trainer"]

    # TODO(should we do this every episode or every training iteration)?
    # trainer.workers.foreach_worker(
    #     lambda ev: ev.foreach_env(
    #         lambda env: env.select_new_adversary()))


def on_episode_end(info):
    """Select the currently active adversary"""

    # store info about how many adversaries there are
    if hasattr(info["env"], 'envs'):

        env = info["env"].envs[0]
        episode = info["episode"]
        if hasattr(env, 'num_correct_guesses'):
            prediction = env.num_correct_guesses / env.horizon
            episode.custom_metrics["correct_pred_frac"] = prediction

        if hasattr(env, 'state_error'):
            state_list = env.state_error / env.horizon
            # Track the mean error in every element of the state
            state_err_dict = {"state_err_{}".format(i): sum_state for i, sum_state in enumerate(state_list)}

            for key, val in state_err_dict.items():
                episode.custom_metrics[key] = val

        if hasattr(env, 'select_new_adversary'):
            for env in info["env"]:
                env.select_new_adversary()
    elif hasattr(info["env"], 'vector_env'):
        envs = info["env"].vector_env.envs
        if hasattr(envs[0], 'num_correct_guesses'):

            prediction_list = [env.num_correct_guesses / env.horizon for env in envs]
            # some of the envs won't actually be used if we are vectorizing so lets just ignore them
            prediction_list = [prediction for env, prediction in zip(envs, prediction_list) if env.step_num != 0]
            info["episode"].custom_metrics["correct_pred_frac"] = np.mean(prediction_list)

        if hasattr(envs[0], 'state_error'):
            state_list = [env.state_error / env.horizon for env in envs]
            sum_states = reduce(lambda x, y: x+y, state_list) / len(envs)
            # Track the mean error in every element of the state
            state_err_dict = {"state_err_{}".format(i): sum_state for i, sum_state in enumerate(sum_states)}

            for key, val in state_err_dict.items():
                info["episode"].custom_metrics[key] = val
        # get the new adversary
        for env in envs:
            if hasattr(env, 'select_new_adversary'):
                env.select_new_adversary()
    else:
        sys.exit("You aren't recording any custom metrics, something is wrong")

    episode = info['episode']
    if "true_rew" in episode.user_data:
        true_rew = np.sum(episode.user_data["true_rew"])
        episode.custom_metrics["true_rew"] = true_rew


if __name__ == "__main__":

    exp_dict, args = setup_exps(sys.argv[1:])

    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone('US/Pacific')).strftime("%m-%d-%Y")
    s3_string = 's3://sim2real/pendulum/' \
                + date + '/' + args.exp_title
    if args.use_s3:
        exp_dict['upload_dir'] = s3_string

    if args.multi_node:
        ray.init(redis_address='localhost:6379')
    elif args.local_mode:
        ray.init(local_mode=True)
    else:
        ray.init()

    run_tune(**exp_dict, queue_trials=False)

    # Now we add code to loop through the results and create scores of the results
    if args.run_transfer_tests:
        output_path = os.path.join(os.path.join(os.path.expanduser('~/transfer_results/pendulum'), date), args.exp_title)
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        for (dirpath, dirnames, filenames) in os.walk(os.path.expanduser("~/ray_results")):
            if "checkpoint_{}".format(args.num_iters) in dirpath:
                # grab the experiment name
                folder = os.path.dirname(dirpath)
                tune_name = folder.split("/")[-1]
                outer_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                script_path = os.path.expanduser(os.path.join(outer_folder, "visualize/transfer_test.py"))
                config, checkpoint_path = get_config_from_path(folder, str(args.num_iters))

                run_transfer_tests(config, checkpoint_path, 100, args.exp_title, output_path)
                if args.num_adv > 0:

                    if not args.model_based:
                        visualize_adversaries(config, checkpoint_path, 10, 200, output_path)

                    if args.model_based:
                        visualize_model_perf(config, checkpoint_path, 10,  25, output_path)

                    if args.use_s3:
                        p1 = subprocess.Popen("aws s3 sync {} {}".format(output_path,
                                                                         "s3://sim2real/transfer_results/pendulum/{}/{}/{}".format(date,
                                                                                                                          args.exp_title,
                                                                                                                          tune_name)).split(
                            ' '))
                        p1.wait()
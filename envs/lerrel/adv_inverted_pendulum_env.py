import gym
from gym import spaces
from gym.utils import seeding
from gym.envs.mujoco.inverted_pendulum import InvertedPendulumEnv
from gym.spaces import Box, Discrete
import numpy as np
from os import path
from ray.rllib.env.multi_agent_env import MultiAgentEnv

class AdvMAPendulumEnv(InvertedPendulumEnv, MultiAgentEnv):
    def __init__(self, config):
        self.num_adversaries = config["num_adversaries"]
        self.adversary_strength = config["adversary_strength"]
        self.curr_adversary = np.random.randint(low=0, high=self.num_adversaries)
        super(AdvMAPendulumEnv, self).__init__()
        self._adv_f_bname = 'pole'
        bnames = self.model.body_names
        self._adv_bindex = bnames.index(self._adv_f_bname) #Index of the body on which the adversary force will be applied

    @property
    def adv_action_space(self):
        """ 2D adversarial action. Maximum of self.adversary_strength in each dimension.
        """
        return Box(low=-self.adversary_strength, high=self.adversary_strength, shape=(2,))

    @property
    def adv_observation_space(self):
        return self.observation_space

    def _adv_to_xfrc(self, adv_act):
        self.sim.data.xfrc_applied[self._adv_bindex][0] = adv_act[0]
        self.sim.data.xfrc_applied[self._adv_bindex][2] = adv_act[1]

    def select_new_adversary(self):
        self.curr_adversary = np.random.randint(low=0, high=self.num_adversaries)

    def step(self, actions):
        if isinstance(actions, dict):
            pendulum_action = actions['pendulum']

            if 'adversary{}'.format(self.curr_adversary) in actions.keys():
                adv_action = actions['adversary{}'.format(self.curr_adversary)]
                self._adv_to_xfrc(adv_action)
        else:
            assert actions in self.action_space
            pendulum_action = actions
        
        reward = 1.0
        self.do_simulation(pendulum_action, self.frame_skip)
        ob = self._get_obs()
        notdone = np.isfinite(ob).all() and (np.abs(ob[1]) <= .2)
        done = not notdone
        
        if isinstance(actions, dict):
            info = {'pendulum': {'pendulum_reward': reward}}
            obs_dict = {'pendulum': ob}
            reward_dict = {'pendulum': reward}

            for i in range(self.num_adversaries):
                # is_active = 1 if self.curr_adversary == i else 0
                obs_dict.update({
                    'adversary{}'.format(i): ob
                })

                reward_dict.update({'adversary{}'.format(i): -reward})

            done_dict = {'__all__': done}
            return obs_dict, reward_dict, done_dict, info
        else:
            return ob, reward, done, {}     

    def reset(self):
        obs = super().reset()
        curr_obs = {'pendulum': obs}
        for i in range(self.num_adversaries):
            is_active = 1 if self.curr_adversary == i else 0
            curr_obs.update({'adversary{}'.format(i):
                                 obs})

        return curr_obs

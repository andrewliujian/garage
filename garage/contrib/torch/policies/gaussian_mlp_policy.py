import math

import torch
import torch.nn as nn
from torch.distributions.normal import Normal

from garage.contrib.exp.core import Policy
from garage.contrib.torch.core.mlp import MLP



class GaussianMLPPolicy(nn.Module, Policy):
    def __init__(self,
                 env_spec,
                 hidden_sizes=(32,32),
                 learn_std=True,
                 init_std=1.0,
                 adaptive_std=False,
                 hidden_nonlinearity=torch.tanh,
                 output_nonlinearity=torch.tanh):
        """
        Diagonal MLP Gaussian policies.

        Args:
            env_spec: Observation and action spec of gym environment.
            hidden_sizes: Hidden layer size of MLP.
            learn_std: Learn variance of Gaussian.
            init_std: Intialial standard variance of Gaussian.
            adaptive_std: Use MLP to learn variance from observation.
            hidden_nonlinearity: MLP hidden layer activation function.
            output_nonlinearity: MLP output layer activation function.
        """
        if adaptive_std:
            raise NotImplementedError

        nn.Module.__init__()

        obs_dim = env_spec.observation_space.flat_dim
        action_dim = env_spec.action_space.flat_dim

        self.mu = MLP(
            obs_dim, action_dim, hidden_sizes,
            hidden_nonlinearity, output_nonlinearity)
        self.log_std = nn.Parameter(math.log(init_std) * torch.ones(action_dim, dtype=torch.float32))

    def forward(self, obs):
        return self.sample(obs)

    def sample(self, obs):
        actions = self.policy(obs).sample()
        logpdf = self.logpdf(actions)
        return actions, logpdf

    def logpdf(self, obs, action):
        return self.policy(obs).log_prob(action).sum(dim=1)

    def policy(self, obs):
        return Normal(self.mu(obs), self.log_std.exp())

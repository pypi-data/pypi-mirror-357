'''
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Copyright (C) 2025, Intelligent Control Systems Group, ETH Zurich
%
% This code is made available under an MIT License (see LICENSE file).
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
'''

from collections.abc import Callable
from dataclasses import dataclass
import numpy as np

from ampyc.typing import Noise
from ampyc.params import ParamsBase
from ampyc.noise import PolytopeNoise
from ampyc.utils import Polytope


class TestParams(ParamsBase):
    '''
    Default parameters for experiments with a robust and a stochastic constraint tightening MPC controller.
    '''

    @dataclass
    class ctrl:
        name: str = 'testing'
        N: int = 10
        Q: np.ndarray = 100 * np.eye(2)
        R: np.ndarray = 10 * np.eye(1)

    @dataclass
    class sys:
        # system dimensions
        n: int = 2
        m: int = 1

        # dynamics matrices
        A: np.ndarray = np.array(
            [
                [1.0, 0.15],
                [0.0, 1.0]
            ])
        B: np.ndarray = np.array([0.5, 0.5]).reshape(-1,1)
        C: np.ndarray = np.eye(n)
        D: np.ndarray = np.zeros((n,m))

        # state constraints
        A_x: np.ndarray | None = np.array(
            [
                [1, 0], 
                [-1, 0],
                [0, 1],
                [0, -1]
            ])
        b_x: np.ndarray | None = np.array([0.5, 1.5, 1.5, 1.5]).reshape(-1,1)

        # input constraints
        A_u: np.ndarray | None = np.array([1, -1]).reshape(-1,1)
        b_u: np.ndarray | None = np.array([1, 1]).reshape(-1,1)

        # noise description
        sig_w: float = 0.1
        A_w: np.ndarray | None = np.array(
            [
                [1, 0], 
                [-1, 0],
                [0, 1],
                [0, -1]
            ])
        b_w: np.ndarray | None = np.array([sig_w, sig_w, 0.1, 0.1]).reshape(-1,1)

        # noise generator
        noise_generator: Noise = PolytopeNoise(Polytope(A_w, b_w))

        def __post_init__(self) -> None:
            '''
            Post-initialization: ensure that derived attributes, i.e., parameters that are computed from other static parameters,
            are set correctly.
            '''
            # dynamics matrices
            self.b_w = np.array([self.sig_w, self.sig_w, 0.1, 0.1]).reshape(-1,1)

            # noise generator
            self.noise_generator = PolytopeNoise(Polytope(self.A_w, self.b_w))
    
    @dataclass
    class sim:
        num_steps: int = 30
        num_traj: int = 50
        x_0: np.ndarray = np.array([np.deg2rad(20), np.deg2rad(-5)]).reshape(-1,1)

    @dataclass
    class plot:
        color: str = 'blue'
        alpha: float | Callable = lambda i: 0.5/(1 + i**(0.5))
        linewidth: float = 1.0

import numpy as np
from typing import Tuple
from .algorithm import Algorithm

class Extragradient(Algorithm):
    def __init__(self, gamma: float, alpha: float, type: str = "unconstrained"):
        if type == "unconstrained":
            super().__init__(1, 1, [2], [], [1]) 
        else:
            raise ValueError("Not valid type/implemented yet")
        self.type = type
        self.gamma = gamma
        self.alpha = alpha
    
    def set_gamma(self, gamma):
        self.gamma = gamma
    
    def set_alpha(self, alpha):
        self.alpha = alpha
    
    def get_ABCD(self, k: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        if self.type == "unconstrained":
            A = np.array([[1]])
            B = np.array([[0, -self.alpha]])
            C = np.array([[1], [1]])
            D = np.array([[0, 0], 
                          [-self.gamma, 0]])
        else:
            raise ValueError("Not valid type/implemented yet")
        return (A, B, C, D)
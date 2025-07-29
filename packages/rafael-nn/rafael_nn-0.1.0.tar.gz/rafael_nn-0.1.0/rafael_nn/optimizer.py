import numpy as np
from abc import ABC, abstractmethod

class Optimizer(ABC):
    @abstractmethod
    def update(self, weights: np.ndarray, gradients: np.ndarray, layer_index: int) -> np.ndarray:
        pass


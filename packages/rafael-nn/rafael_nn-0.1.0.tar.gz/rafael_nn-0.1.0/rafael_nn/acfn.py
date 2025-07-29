import numpy as np
from abc import ABC, abstractmethod

class ActivationFunction(ABC):
    @abstractmethod
    def initialization(self, x: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def forward(self, x: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def backward(self, x: np.ndarray) -> np.ndarray:
        pass

class ReLU(ActivationFunction):
    def initialization(self, x: np.ndarray) -> np.ndarray:
        pass

    def forward(self,x:np.ndarray):
        return x.clip(0)

    def backward(self,x:np.ndarray):
        return x.clip(0)


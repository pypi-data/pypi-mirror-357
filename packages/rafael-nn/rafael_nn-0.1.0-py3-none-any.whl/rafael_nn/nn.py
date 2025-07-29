import numpy as np
from abc import ABC, abstractmethod
from tarea1.experiment.optimizer import Optimizer

class Layer(ABC):
    @abstractmethod
    def forward(self, input: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def backward(self, grad_output: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def update_params(self, optimizer: Optimizer, layer_index: int) -> None:
        pass


class NeuralNetwork:
    def __init__(self):
        self.layers: list[Layer] = []

    def add(self, layer: Layer) -> None:
        pass

    def forward(self, x: np.ndarray) -> np.ndarray:
        pass

    def backward(self, loss_grad: np.ndarray) -> None:
        pass

    def update(self, optimizer: Optimizer) -> None:
        pass

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int, batch_size: int, loss_fn, optimizer: Optimizer) -> None:
        pass

    def predict(self, X: np.ndarray) -> np.ndarray:
        pass

"""
This mmodule contains the neural network neuron classes.
"""

from numpy import array, matmul, ndarray, random

from snoscience._activation import sigmoid, sigmoid_prime


class Neuron:
    """
    Default neuron class.
    """

    def __init__(self, weights: int):
        """
        Parameters
        ----------
        weights: int
            Number of weights to add to the neuron.
        """
        self.x = array([])
        self.y = array([])
        self.y_prime = array([])

        self.weights = 0.01 * random.random(size=(weights, 1))
        self.bias = 0.01 * random.rand()

        self.total_weights = array([])
        self.total_bias = float()
        self.position = int()

        self.activation = {"sigmoid": {"function": sigmoid, "derivative": sigmoid_prime}}
        self.optimiser = {"SGD": self.sgd}

    def calculate_x(self, previous: ndarray) -> None:
        """
        Calculate the neuron input float based on the output of the previous layer.

        Parameters
        ----------
        previous: ndarray
            Output from the previous layer.
        """
        self.x = matmul(previous, self.weights) + self.bias

    def calculate_y(self, activation: str) -> None:
        """
        Calculate the neuron output vector based on its current input.

        Parameters
        ----------
        activation: str
            Activation function to be used.
        """
        self.y = self.activation[activation]["function"](x=self.x)

    def calculate_y_prime(self, activation: str) -> None:
        """
        Calculate the neuron output derivative vector based on its current input.

        Parameters
        ----------
        activation: str
            Activation function to be used.
            Supported functions: sigmoid.
        """
        self.y_prime = self.activation[activation]["derivative"](x=self.x)

    def train(self, optimiser: str, **kwargs) -> None:
        """
        Train the neuron with the given optimiser.

        Parameters
        ----------
        optimiser: str
            Optimiser to train the neuron with.
        kwargs
            Optimiser hyperparameters as keyword arguments.
        """
        self.optimiser[optimiser](**kwargs)

    def sgd(self, rate: float) -> None:
        """
        Train the neuron based on the stochastic gradient descent method.

        Parameters
        ----------
        rate: float
            Learning rate.
        """
        self.bias = self.bias - (rate * self.total_bias)
        self.weights = self.weights - (rate * self.total_weights)

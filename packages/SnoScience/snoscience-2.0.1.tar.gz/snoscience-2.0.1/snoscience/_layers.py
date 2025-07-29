"""
This module contains the neural network layer classes.
"""

from typing import Union

from numpy import array, hstack, ndarray, sum as numpy_sum, zeros

from ._neurons import Neuron


class BasicLayer:
    """
    Simplified layer class used for input and loss layers.
    """

    def __init__(self):
        self.y = array([0.0])
        self.y_prime = array([0.0])

        self.previous: Union[BasicLayer, Layer, None] = None
        self.next: Union[BasicLayer, Layer, None] = None


class Layer(BasicLayer):
    """
    Default layer class used for hidden and output layers consisting of neuron instances.
    """

    def __init__(self, activation: str):
        """
        Parameters
        ----------
        activation: str
            Applied activation functions for neurons in this layer.
        """
        super().__init__()

        self.previous: Union[BasicLayer, Layer] = BasicLayer()
        self.next: Union[BasicLayer, Layer] = BasicLayer()

        self.activation = activation
        self.neurons: list[Neuron] = []

    def add_neurons(self, neurons: int, weights: int) -> None:
        """
        Add neurons to this layer.

        Parameters
        ----------
        neurons: int
            Number of neurons to add to this layer.
        weights: int
            Number of weights per neuron.
        """
        self.neurons = [Neuron(weights=weights) for _ in range(neurons)]

        for i, neuron in enumerate(self.neurons):
            neuron.position = i

    def train_neurons(self, optimiser: str, **kwargs) -> None:
        """
        Run the "train" method for each neuron in this layer.

        Parameters
        ----------
        optimiser: str
            Optimiser to train the neurons with.
        kwargs
            Optimiser hyperparameters as keyword arguments.
        """
        if optimiser == "SGD":
            self.calculate_total()

        for neuron in self.neurons:
            neuron.train(optimiser=optimiser, **kwargs)

    def calculate_x(self) -> None:
        """
        Run the "calculate_x" method for each neuron in this layer.
        """
        for neuron in self.neurons:
            neuron.calculate_x(previous=self.previous.y)

    def calculate_y(self) -> None:
        """
        Run the "calculate_y" method for each neuron in this layer.

        Afterward, stack all neuron outputs vectors to create the layer output matrix.
        """
        for neuron in self.neurons:
            neuron.calculate_y(activation=self.activation)

        self.y = hstack(tup=[neuron.y for neuron in self.neurons])

    def calculate_y_prime(self) -> None:
        """
        Run the "calculate_y_prime" method for each neuron in this layer.
        """
        for neuron in self.neurons:
            neuron.calculate_y_prime(activation=self.activation)

    def calculate_total(self) -> None:
        """
        Calculate the total derivative vector for the neuron's weights, and the total derivative float for the neuron's
        bias for each neuron in this layer.
        """
        for neuron in self.neurons:
            total = self.calculate_total_neuron(neuron=neuron, start=neuron, position=neuron.position)

            neuron.total_weights = numpy_sum(total * self.previous.y, axis=0).reshape(-1, 1)
            neuron.total_bias = numpy_sum(total)

    def calculate_total_layer(self, start: Neuron, position: int) -> ndarray:
        """
        Calculate the partial derivative vectors for each neuron in this layer and sum them. This is used by the
        "calculate_total_neuron" method to continue recursion through the network.

        Parameters
        ----------
        start: Neuron
            The neuron from which the recursion is started.
        position: int
            Position of the neuron in this layer.

        Returns
        -------
        total: ndarray
            Summed neuron partial derivatives.
        """
        total = zeros(shape=start.x.shape)

        for neuron in self.neurons:
            total = total + self.calculate_total_neuron(neuron=neuron, start=start, position=position)

        return total

    def calculate_total_neuron(self, neuron: Neuron, start: Neuron, position: int) -> ndarray:
        """
        Calculate the total derivative vector for the neuron. This is used by the "calculate_total" method to start
        recursion through the network, and by the "calculate_total_layer" method to continue recursion.

        Parameters
        ----------
        neuron: Neuron
            The neuron whose total derivative needs to be calculated.
        start: Neuron
            The neuron from which the recursion is started.
        position: int
            Position of the neuron in this layer.

        Returns
        -------
        total: ndarray
            Total derivative for the neuron.

        Notes
        -----
        pylint "no-member" error disabled:
            BasicLayer instances are filtered in the if-statement.
        """
        if start != neuron:
            first = neuron.y_prime * neuron.weights[position, 0]
        else:
            first = neuron.y_prime

        # pylint: disable=no-member
        if not isinstance(self.next, Layer):
            second = self.next.y_prime[:, neuron.position].reshape(-1, 1)
        else:
            second = self.next.calculate_total_layer(start=start, position=neuron.position)
        # pylint: enable=no-member

        return first * second

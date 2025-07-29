"""
This module contains the neural network classes.
"""

from numpy import arange, argmax, ndarray, random, round as numpy_round, zeros

from snoscience._layers import BasicLayer, Layer
from snoscience._loss import mse_prime


class NeuralNetwork:
    """
    Sequential feed-forward neural network consisting of layer instances.
    """

    _SUPPORTED = {"activation": ["sigmoid"], "loss": ["MSE"], "optimiser": ["SGD"]}

    _LOSS = {"MSE": mse_prime}

    def __init__(self, inputs: int, loss: str = "MSE", optimiser: str = "SGD"):
        """
        Parameters
        ----------
        inputs: int
            Number of inputs per sample.
        loss: str
            Loss function to use when training the network.
        optimiser: str:
            Optimiser to use when training the network.

        Raises
        ------
        ValueError
            Loss function is not supported.
        ValueError
            Optimiser is not supported.
        """
        self._inputs = inputs
        self._layers: list[Layer] = []
        self._outputs = 0

        if loss not in self._SUPPORTED["loss"]:
            raise ValueError("Loss function is not supported.")

        if optimiser not in self._SUPPORTED["optimiser"]:
            raise ValueError("Optimiser is not supported.")

        self._loss = self._LOSS[loss]
        self._optimiser = optimiser

    def add_layer(self, neurons: int, activation: str = "sigmoid") -> None:
        """
        Add a layer to the neural network.

        Parameters
        ----------
        neurons: int
            Number of neurons to add to the layer.
        activation: str
            Activation function to use in the layer.

        Raises
        ------
        ValueError
            Activation function is not supported.
        """
        if activation not in self._SUPPORTED["activation"]:
            raise ValueError("Activation function is not supported.")

        layer = Layer(activation=activation)

        if not self._layers:
            layer.previous = BasicLayer()
            weights = self._inputs
        else:
            layer.previous = self._layers[-1]
            weights = len(self._layers[-1].neurons)

        layer.previous.next = layer
        layer.add_neurons(neurons=neurons, weights=weights)

        self._layers.append(layer)
        self._outputs = neurons

    def predict(self, x: ndarray, classify: bool) -> ndarray:
        """
        Let the neural network predict the outputs from the given inputs.

        Parameters
        ----------
        x: ndarray
            Inputs for the network.
        classify: bool
            Create classification from output layer, otherwise keep regression.

        Returns
        -------
        predictions: ndarray
            Output predictions from the network.

        Raises
        ------
        ValueError
            Size of the input array does not match with the network inputs.
        ValueError
            No layers are present in the network.
        """
        if x.shape[-1] != self._inputs:
            raise ValueError("Size of the input array does not match with the network inputs.")
        if not self._layers:
            raise ValueError("No layers are present in the network.")

        self._layers[0].previous.y = x

        for layer in self._layers:
            layer.calculate_x()
            layer.calculate_y()

        predictions = self._layers[-1].y

        # Create classification from output layer, otherwise keep regression.
        if classify:
            # Select likeliest case per row if multi classification.
            if predictions.shape[-1] > 1:
                # Select index with maximum value per row (if multiple first index is taken).
                maximums = argmax(predictions, axis=1)

                # Create new array with zeros.
                predictions = zeros(shape=predictions.shape)

                # Set indices with maximum elements to one.
                predictions[arange(predictions.shape[0]), maximums] = 1

            # Simply round outputs if binary classification.
            else:
                predictions = numpy_round(predictions)

        return predictions

    def train(self, x: ndarray, y: ndarray, epochs: int, samples: int, **kwargs) -> None:
        """
        Train the neural network with the given parameters.

        Parameters
        ----------
        x: ndarray
            Input samples to train the network with.
        y: ndarray
            Output samples to train the network with.
        epochs: int
            Number of training iterations.
        samples: int
            Number of samples taken from the dataset per iteration.
        kwargs: Any
            Optimiser hyperparameters as keyword arguments.

        Raises
        ------
        ValueError
            Size of the input array does not match with the network inputs.
        ValueError
            No layers are present in the network.
        ValueError
            Size of the output array does not match with the network outputs.
        ValueError
            Number of samples per epoch is larger than dataset.
        KeyError
            Hyperparameters required for optimiser are not given as kwargs.
        """
        if x.shape[-1] != self._inputs:
            raise ValueError("Size of the input array does not match with the network inputs.")
        if not self._layers:
            raise ValueError("No layers are present in the network.")
        if y.shape[-1] != self._outputs:
            raise ValueError("Size of the output array does not match with the network outputs.")
        if samples > len(x):
            raise ValueError("Number of samples per epoch is larger than dataset.")

        if self._optimiser == "SGD":
            if "rate" not in kwargs:
                raise KeyError("Hyperparameters required for optimiser are not given as kwargs.")

        self._layers[-1].next = BasicLayer()

        for _ in range(epochs):
            section = random.choice(a=len(x), size=samples, replace=False)
            section_x = x[section, :]
            section_y = y[section, :]

            self._layers[0].previous.y = section_x

            for layer in self._layers:
                layer.calculate_x()
                layer.calculate_y()
                layer.calculate_y_prime()

            self._layers[-1].next.y_prime = self._loss(calc=self._layers[-1].y, true=section_y)

            for layer in self._layers:
                layer.train_neurons(optimiser=self._optimiser, **kwargs)

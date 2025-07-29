"""
This module contains the supported activation functions with their derivatives.
"""

from numpy import exp, ndarray


def sigmoid(x: ndarray) -> ndarray:
    """
    Calculate the sigmoid output matrix based on the given input.

    Parameters
    ----------
    x: ndarray
        Input for the sigmoid function.

    Returns
    -------
    sigmoid: ndarray
        Output from the sigmoid function.
    """
    return 1 / (1 + exp(-x))


def sigmoid_prime(x: ndarray) -> ndarray:
    """
    Calculate the sigmoid derivative matrix based on the given input.

    Parameters
    ----------
    x: ndarray
        Input for the sigmoid derivative.

    Returns
    -------
    sigmoid_prime: ndarray
        Output from the sigmoid derivative.
    """
    y = sigmoid(x=x)
    return y * (1 - y)

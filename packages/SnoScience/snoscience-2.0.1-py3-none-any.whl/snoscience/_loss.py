"""
This module contains the supported loss functions with their derivatives.
"""

from numpy import ndarray, sum as numpy_sum


def mse(calc: ndarray, true: ndarray) -> ndarray:
    """
    Calculate the mean squared error per output vector from the given matrices.

    Parameters
    ----------
    calc: ndarray
        Vector containing all the calculated or predicted values.
    true: ndarray
        Vector containing all the true or expected values.

    Returns
    -------
    mse: ndarray
        Mean squared error per output.
    """
    squared_error = (true - calc) ** 2
    return numpy_sum(squared_error / len(squared_error), axis=0)


def mse_prime(calc: ndarray, true: ndarray) -> ndarray:
    """
    Calculate the mean squared error derivative matrix from the given matrices.

    Parameters
    ----------
    calc: ndarray
        Array containing all the calculated or predicted values.
    true: ndarray
        Array containing all the true or expected values.

    Returns
    -------
    mse_prime: ndarray
        Mean squared error derivative array.
    """
    return -2 * (true - calc)

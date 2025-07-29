"""
This module contains functions to calculate network performance.
"""

from numpy import count_nonzero, ndarray, round as numpy_round

from snoscience._loss import mse


def calculate_mse(calc: ndarray, true: ndarray) -> ndarray:
    """
    Calculate the mean squared error per output vector from the given matrices.

    Parameters
    ----------
    calc: ndarray
        Array containing all the calculated or predicted values.
    true: ndarray
        Array containing all the true or expected values.

    Returns
    -------
    mse: ndarray
        Mean squared error per output.
    """
    return numpy_round(mse(calc=calc, true=true), decimals=4)


def calculate_accuracy(calc: ndarray, true: ndarray) -> float:
    """
    Calculate the accuracy percentage from the given matrices.

    Parameters
    ----------
    calc: ndarray
        Array containing all the calculated or predicted values.
    true: ndarray
        Array containing all the true or expected values.

    Returns
    -------
    accuracy: float
        Accuracy percentage.
    """
    misses = numpy_round(true - calc, decimals=1)
    misses = count_nonzero(misses, axis=1)
    misses = count_nonzero(misses)

    accuracy = (1 - (misses / len(true))) * 100
    return float(numpy_round(accuracy, decimals=2))

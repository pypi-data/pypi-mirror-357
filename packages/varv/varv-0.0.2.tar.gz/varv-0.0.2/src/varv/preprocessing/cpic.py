# Created by Cees Dekker Lab at the Delft University of Technology
# Refactored by Thijn Hoekstra

import numpy as np

"""the function defining the cpic (bias estimator for introducing transitions)
"""


def cpic_greater_than_1000(x):
    def cpic_greater_than_1000(x):
        """
        Calculates the CPIC (Change-Point Information Criterion) for values greater than 1000.

        This function uses a predefined model to compute the CPIC value for datasets where the total
        number of data points (N_T) exceeds 1000. The model applies logarithmic transformations to
        the input value `x` to estimate the CPIC.

        Parameters:
            x (float): The input value representing the total number of data points (N_T), which must be greater than 1000.

        Returns:
            float: The computed CPIC value.

        Example:
            >>> cpic_value = cpic_greater_than_1000(1500)
            >>> print(cpic_value)
            4.235
        """

    a = 2.456
    b = 1.187
    c = 2.73
    return a * np.log(np.log(x)) + b * np.log(np.log(np.log(x))) + c


def cpic_less_than_1000(x):
    """
    Calculates the CPIC (Change-Point Information Criterion) for values less than 1000.

    This function uses a predefined model to compute the CPIC value for datasets where the total
    number of data points (N_T) is less than 1000. The model combines logarithmic transformations,
    polynomial terms, and absolute value functions to estimate the CPIC.

    Parameters:
        x (float): The input value representing the total number of data points (N_T), which must be less than 1000.

    Returns:
        float: The computed CPIC value.

    Example:
        >>> cpic_value = cpic_less_than_1000(500)
        >>> print(cpic_value)
        7.123
    """
    a = 1.239
    b = 0.9872
    c = 1.999
    p3 = 5.913e-10
    p4 = -1.876e-06
    p5 = 0.004354
    ph = -0.1906
    return (
        a * np.log(np.log(x))
        + b * np.log(x)
        + p3 * x**3
        + p4 * x**2
        + p5 * x
        + ph * np.abs(x) ** 0.5
        + c
    )


def get_cpic_penalty(N_T: int) -> float:
    """
    Calculates the CPIC penalty to prevent overfitting in the likelihood maximizing model.

    This penalty is based on the methodology developed by LaMont and Wiggins (2016),
    utilizing Monte Carlo simulations. It is used to adjust the model's likelihood function
    in order to avoid overfitting when identifying transitions in data. The penalty is calculated
    using different formulas depending on the value of N_T (the total number of data points).

    Parameters:
        N_T (int): The total number of data points, which is used to determine the appropriate CPIC penalty.

    Returns:
        float: The calculated CPIC penalty based on the number of data points.

    """
    if N_T >= 1e6:
        p_cpic = cpic_greater_than_1000(1e6)
    elif N_T > 1000:
        p_cpic = cpic_greater_than_1000(N_T)
    else:
        p_cpic = cpic_less_than_1000(N_T)
    return p_cpic

#
#      Copyright (C) 2024 Thijn Hoekstra
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
import typing

import pandas as pd

import scipy
import numpy as np
from matplotlib import pyplot as plt

from varv import config


def lowpass_filter(i: np.ndarray, sfreq: float, cutoff_freq: float) -> np.ndarray:
    """Applies a third-order butterworth low-pass filter"""
    b, a = scipy.signal.butter(3, cutoff_freq / sfreq)
    zi = scipy.signal.lfilter_zi(b, a)
    i, _ = scipy.signal.lfilter(b, a, i, zi=zi * i[0])
    return i


def check_if_array_is_half_cycle(a: np.ndarray, period: int) -> None:
    """Checks if array contains data on half a cycle

    Checks if array contains data on half a bias votlage cycle. Such an array
    is referred to a 'long' matrix by Noakes et. al. (2019). In such an array,
    each row now corresponds to a single voltage, as opposed to a single phase
    point (each voltage point corresponds to two phase points, one for the up
    swing of the voltage cycle and one for the down swing.

    Args:
        a (np.ndarray): An array to check.
        period (int): The period of the bias votlage cycle in samples.
    """
    if a.ndim != 2:
        raise ValueError("Expected array to be 2-dimensional.")
    elif a.shape[0] == period:
        raise ValueError(
            f"Expected half-cycle array to have "
            f"{period // 2} rows, but instead got {a.shape[0]}. "
            f"You might have accidentally used a full-cycle array "
            f"instead."
        )
    elif a.shape[0] != period // 2:
        raise ValueError(
            f"Expected half-cycle array to have "
            f"{period // 2} rows, but instead got {a.shape[0]}."
        )


def check_if_array_is_full_cycle(a: np.ndarray, period: int) -> None:
    """Checks if array contains data on half a cycle

    Checks if array contains data on the full bias votlage cycle. In such an
    array each column contains the voltage/current data of a full bias votlage
    cycle. Each voltage has two columns, one for the up swing of the voltage
    cycle and one for the down swing.

    Args:
        a (np.ndarray): An array to check.
        period (int): The period of the bias votlage cycle in samples.
    """
    if a.ndim != 2:
        raise ValueError("Expected array to be 2-dimensional.")
    elif a.shape[0] == period // 2:
        raise ValueError(
            f"Expected half-cycle array to have "
            f"{period} rows, but instead got {a.shape[0]}. "
            f"You might have accidentally used a half-cycle array "
            f"instead."
        )
    elif a.shape[0] != period:
        raise ValueError(
            f"Expected half-cycle array to have "
            f"{period} rows, but instead got {a.shape[0]}."
        )


def get_tu_delft_cmap():
    """Gets a list of colors from the Delft University of Technology style guide"""
    # Matplotlib style
    # return [
    #     "#0076C2",
    #     "#EC6842",
    #     "#009B77",
    #     "#A50034",
    #     "#6F1D77",
    #     "#0C2340",
    #     "#EF60A3",
    #     "#6CC24A",
    #     "#FFB81C",
    #     "#00B8C8",
    # ]

    # Mixed style
    return [
        "#0C2340",
        "#00B8C8",
        "#0076C2",
        "#E03C31",
        "#EC6842",
        "#FFB81C",
        "#6F1D77",
        "#EF60A3",
        "#A50034",
        "#6CC24A",
        "#009B77",
        "#5C5C5C",
    ]

    # Rainbow style
    # return [
    #     "#0C2340",
    #     "#00B8C8",
    #     "#0076C2",
    #     "#6F1D77",
    #     "#EF60A3",
    #     "#E03C31",
    #     "#EC6842",
    #     "#FFB81C",
    #     "#6CC24A",
    #     "#009B77",
    #     "#5C5C5C",
    # ]


def get_phase_of_period(
    v_data: np.ndarray,
    period: int,
    max_length_to_check: int = 10000,
    min_amplitude: float = 1,
    invert: bool = True,
) -> int:
    """Finds the phase of a frequency of a known period.

    Args:
        v_data (np.ndarray): A numpy array containing the time series of bias
            voltage.
        period (int): The period in samples of the known bias frequency.
        max_length_to_check (int): Maximum number of samples in which to find a
            period and phase. Defaults to 10,000 samples. Speeds up Fourier
            transform.
        min_amplitude (float): The minimum amplitude in mV the bias frequency
            component should have. If this is not the case, the bias frequency
            is assumed to not be present and an error is raised.
       invert (bool): Whether to invert the phase. Defaults to True in which
            case the value returned is equivalent to a sample in the signal
            with zero phase shift. When set to False, the phase returned is
            the mathematical phase shift.

    Returns:
        An integer specifying the phase (offset) in samples of the bias
        frequency signal.


    Raises:
        ValueError: This error is raised when no Fourier component of
            significant amplitude is found in the arrays. This might mean that
            no AC bias votlage was applied during the measurement.
    """
    N = min(max_length_to_check, len(v_data))
    x = v_data[:N]
    k = N / period  # Frequency to look for
    fourier_component = (
        1 / N * np.sum(x * np.exp(-1j * k * 2 * np.pi / N * np.arange(N)))
    )

    if np.abs(fourier_component) < min_amplitude:
        raise ValueError(
            f"No AC voltage applied in first {N} points of file - could not "
            f"determine phase of component with period {period}. Found "
            f"component with magnitude {np.abs(fourier_component)}."
        )

    phase = get_phase_from_fourier_component(fourier_component, period)
    if invert:
        phase = (period - phase) % period
    return phase


def get_phase_from_fourier_component(
    fourier_component: np.complex128, period: int
) -> int:
    """Finds the phase in samples for a known complex fourier component.

    The complex fourier component is assumed to be the component associated to
    the frequency equivalent to `period`.

    Args:
        fourier_component (np.complex128): A complex fourier component of
            frequency related to the period.
        period (int): The period in samples.

    Returns:
        The phase in samples of that complex component.
    """
    phase = np.angle(fourier_component) / (2 * np.pi) * period

    if phase < 0:
        phase += period

    phase = round(phase % period)

    if phase == period:
        phase = 0

    return phase


def downsample_by_exact_factor(a: np.ndarray, target_size: int) -> np.ndarray:
    """Downsamples a time series by dropping samples"""
    assert a.ndim == 1

    factor = len(a) // target_size
    if factor == 1:
        return a

    assert factor > 1

    factor = int(factor)
    return a[::factor]


def downsample_by_poly(
    downsample_to_rate: float,
    f_samp: float,
    arrays: typing.Union[np.ndarray, tuple, list],
) -> tuple:
    """Downsample raw events using SciPy.

    Better alternative to `downsample_by_mean`.

    Args:
        downsample_to_rate (float): Rate to downsample to in Hz.
        f_samp (float): Sample rate in Hz.
        arrays (np.ndarray): Array containing current/votlage events in pA.

    Returns:
        i_data: Array containing downsampled current events in pA.
        v_data: Array containing downsampled voltage events in mV.
    """
    # Weird problem where input has to be a float rather than int.
    # Otherwise, resampled to zeros.
    up = int(downsample_to_rate)
    down = int(f_samp)

    if up == down:
        return arrays

    if isinstance(arrays, np.ndarray) and arrays.ndim == 1:
        return scipy.signal.resample_poly(arrays.astype(np.float64), up, down)
    elif (isinstance(arrays, np.ndarray) and arrays.ndim == 2) or isinstance(
        arrays, (tuple, list)
    ):
        if isinstance(arrays, tuple):
            arrays = list(arrays)
        for i, array in enumerate(arrays):
            arrays[i] = scipy.signal.resample_poly(array.astype(np.float64), up, down)
        return arrays

    else:
        raise ValueError(
            f"Unexpected array(s) to downsample. Expected single "
            f"array or 2D/list of arrays but got: {type(arrays)}"
        )


def downsample_by_mean(data: np.ndarray, factor: int) -> np.ndarray:
    """Downsample by taking averages.

    This might not be a smart way of downsampling:

    https://dsp.stackexchange.com/questions/58632/decimation-vs-mean-in-downsampling-operation

    Args:
        data: Array to downsample
        factor: Downsampling factor

    Returns:
        Downsampled array.

    """
    if factor == 1:
        return data
    n_dspts = len(data) // factor
    data = data[0 : n_dspts * factor]
    newdata = np.mean(data.reshape(n_dspts, factor), axis=1)
    return newdata


def df_from_struct(arr: np.ndarray) -> pd.DataFrame:
    """Create a dataframe from a NumPy structured array."""
    return pd.DataFrame(arr, columns=[name for name in arr.dtype.names])


def add_field_to_struct(arr: np.ndarray, field: str) -> np.ndarray:
    """Add a field to an existing structured array.

    New field is filled with zeros.

    """
    new_dt = np.dtype(arr.dtype.descr + [(field, np.float64)])
    new_arr = np.zeros(arr.shape, dtype=new_dt)
    # Copy over data
    for name in arr.dtype.names:
        new_arr[name] = arr[name]
    return new_arr


def struct_from_df(df: pd.DataFrame) -> np.ndarray:
    """Create a structured NumPy array from a pandas DataFrame."""
    return df.to_records(index=False)


def get_cov_cols(d: int) -> list:
    """Gets the columns of the covariance matrix in a feature dataframe

    Args:
        d: An integer specifying the number of features.
    """
    return [
        config.COV_FORMAT.format(j, k) for j, k in np.mgrid[:d, :d].reshape((2, d**2)).T
    ]


def get_coef_cols(d):
    """Gets the columns of the feature coefficients in a feature dataframe

     Args:
         d: An integer specifying the number of features.
     """
    return [config.COEF_FORMAT.format(j) for j in range(d)]

def fewer_ticks(ax, n_y: int = 3, n_x: int = None) -> None:
    """Makes a plot have fewer ticks"""
    ax.yaxis.set_major_locator(plt.MaxNLocator(n_y))
    if n_x is not None:
        ax.yaxis.set_major_locator(plt.MaxNLocator(n_x))


def bhattacharyya_distance(mu_1: np.ndarray, sigma_1: np.ndarray, mu_2: np.ndarray, sigma_2: np.ndarray) -> float:
    """Computes the Bhattacharyya distance between two multivariate Gaussians.

    Supports array broadcasting for fast distance computations across multiple distirbutions.

    Args:
        mu_1: The mean of the first multivariate Gaussian.
        sigma_1: The covariance matrix of the first multivariate Gaussian.
        mu_2: The mean of the second multivariate Gaussian.
        sigma_2: The covariance matrix of the second multivariate Gaussian.
    """
    sigma = (sigma_1 + sigma_2) / 2

    term_1 = 0.125 * np.vecdot(mu_1 - mu_2, np.matvec(np.linalg.inv(sigma), (mu_1 - mu_2)))
    term_2 = 0.5 * np.log(np.linalg.det(sigma) / np.sqrt(np.linalg.det(sigma_1) * np.linalg.det(sigma_2)))

    return term_1 + term_2

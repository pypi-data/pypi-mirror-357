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

"""
Capacitance compensation for variable voltage sequencing of peptides.

Based on: Noakes, M.period., Brinkerhoff, H., Laszlo, A.H. et al.
Increasing the accuracy of nanopore DNA sequencing using a time-varying
cross membrane voltage. Nat Biotechnol 37, 651–656 (2019).
https://doi.org/10.1038/s41587-019-0096-0

TODO: Write checks for long matrices etc.
TODO: Find better name for long matrix
"""
import warnings
from importlib import resources as impresources

import pandas as pd
import scipy
import numpy as np
from matplotlib import pyplot as plt

from varv import utils, config
from varv.preprocessing import assets

inp_file_spacing_dna = impresources.files(assets) / "equal_spacing_dna.npz"

SPACING_DNA = np.load(inp_file_spacing_dna)


class CapacitanceCompensationError(Exception):
    pass


def get_compensated_current(
    v_data: np.ndarray,
    i_data: np.ndarray,
    period: int,
    phase: int,
    low_voltage: float = 95,
    high_voltage: float = 205,
    phase_offset: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
    """Returns the compensated current as half-period arrays

    Requires a known period and the phase of the voltage
    """

    v_data = v_data.copy()
    i_data = i_data.copy()

    v_mat_long, i_mat_long = get_half_cycle_matrices_from_arrays(
        v_data, i_data, period, phase, low_voltage, high_voltage, phase_offset
    )

    if v_mat_long.shape[1] == 0:
        raise CapacitanceCompensationError(
            "The voltage sweep does not contain at least one full period of data"
        )

    # Average voltage by voltage point is median along the 2nd dim of long
    # matrix
    v = np.nanmedian(v_mat_long, axis=1)

    # Up slope entries are contained in the top half of the matrix
    # Down slope entries are contained in the bottom half of the matrix
    i_avg_up = np.nanmedian(get_swing(i_mat_long, up=True), axis=1)
    i_avg_do = np.nanmedian(get_swing(i_mat_long, up=False), axis=1)

    # Calculate the correction function from the averaged data
    # Grab voltage, up slope current, and down slope current
    h_v = i_avg_do - i_avg_up

    cropped_v, cropped_hv = crop_data_for_fit(v, h_v)

    if len(cropped_v) < v_mat_long.shape[0] // 10:
        # Usally good cropped residuals around ~62 samples
        raise CapacitanceCompensationError(
            "Cropping the residual failed. This is most likely a badly segmented step."
        )

    params = fit_centered_parabola(cropped_v, cropped_hv)

    m = get_parabola_vertex_y(*params)

    corrector = get_corrector(h_v, m)

    # Tile corrector function
    corrector = np.repeat(corrector.T, i_mat_long.shape[1] // 2, axis=1)

    # Apply the correction function to all the data
    i_comp_mat = i_mat_long + corrector

    return v_mat_long, i_comp_mat


def crop_data_for_fit(v: np.ndarray, h_v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Crops the voltage and asymmetry (H(V)) between the first and third quartiles

    Crop needed to perform a parabolic fit on the lowest point of the asymmetry function H(V).

    """
    q1, q2, q3 = scipy.stats.mstats.mquantiles(v)
    idx_q1 = np.argmin(np.abs(v - q1))
    idx_q3 = np.argmin(np.abs(v - q3))

    return v[idx_q3:idx_q1], h_v[idx_q3:idx_q1]


def get_swing(mat_long: np.ndarray, up=True) -> np.ndarray:
    """Gets the up or down wing of the current from a half-period array"""
    split = mat_long.shape[1] // 2
    if up:
        s = slice(split, None)
    else:
        s = slice(None, split)
    return mat_long[:, s]


def get_half_cycle_matrices_from_arrays(
    v_data: np.ndarray,
    i_data: np.ndarray,
    period: int,
    phase: int,
    low_voltage: float = 95,
    high_voltage: float = 205,
    phase_offset: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """Aligns current and voltage data to a fixed phase and extracts half-periods."""
    # Grab only data where voltage sweep is in range
    v_data[(v_data < low_voltage) | (v_data > high_voltage)] = np.nan

    # Examine to make sure the in-sweep region is at least one period long
    if np.sum(~np.isnan(v_data)) < period:
        raise CapacitanceCompensationError("level does not have full cycle in bounds.")

    v_data = align_data_to_periods(v_data, period, phase)
    i_data = align_data_to_periods(i_data, period, (phase + phase_offset) % period)

    # Difference in length possible due to phase offset
    if len(v_data) > len(i_data):
        i_data = np.concatenate((i_data, np.full(period, np.nan)))
    elif len(v_data) < len(i_data):
        v_data = np.concatenate((v_data, np.full(period, np.nan)))

    cyc = get_number_of_cycles(v_data, period)

    # Reshape v_data into a matrix where each column is the data for one
    # complete cycle
    v_mat = v_data.reshape((cyc, period)).T
    i_mat = i_data.reshape((cyc, period)).T

    v_mat_long = get_half_cycle_mat(v_mat, period)
    i_mat_long = get_half_cycle_mat(i_mat, period)

    return v_mat_long, i_mat_long


def get_conductance(i_comp_mat_long: np.ndarray, v_mat_long: np.ndarray) -> np.ndarray:
    """Calculates the conductance from the current and the voltage"""
    assert i_comp_mat_long.shape[0] == v_mat_long.shape[0], (
        "Unequal number of rows in voltage and current data. Please check "
        "whether both are half-cycle arrays."
    )

    return i_comp_mat_long / v_mat_long


def get_corrector(h_v: np.ndarray, m: float) -> np.ndarray:
    """Calculates the corrector function for the current from the residual and its minimum"""


    # Don't forget V's are arrange from high to low
    # Calculate right half of c_up and left half of c_do
    c_up = np.full_like(h_v, m / 2)
    c_do = np.full_like(h_v, -m / 2)
    # Calculate left half of c_up and right half of c_do
    half = len(h_v) // 2
    c_up[half:] = h_v[half:] - m / 2
    c_do[:half] = m / 2 - h_v[:half]

    # put correction function into the right order to be added into current
    # matrix directly
    corrector = np.vstack([c_do, c_up])
    return corrector


def get_number_of_cycles(v_data: np.ndarray, period: int) -> np.ndarray:
    """Calculates the number of periods in the data"""
    return np.ceil(len(v_data) / period).astype(np.int64)


def align_data_to_periods(v_data, period, phase):
    """
    Aligns voltage data to full cycles by appending NaNs at the beginning and end.

    This function adjusts the input voltage data to align with full cycles of a given `period`
    and `phase`. NaN values are prepended and appended to ensure the data fits neatly into
    complete cycles.

    Args:
        v_data (np.ndarray): A 1D array of voltage data.
        period (int): The length of one cycle in terms of data points.
        phase (int): The phase offset, must be between 0 and `period`.

    Returns:
        np.ndarray: The adjusted voltage data array with NaNs appended to align it to full cycles.

    Raises:
        AssertionError: If the `phase` is not in the range [0, `period`].
    """
    assert 0 <= phase <= period, f"Need phase between 0 and {period}"

    v_data = np.concatenate(
        [
            np.full(phase, np.nan),
            v_data,
            np.full((period - phase - len(v_data) % period) % period, np.nan),
        ]
    )
    return v_data


def get_half_cycle_mat(data_mat: np.ndarray, period: int) -> np.ndarray:
    """
    Converts a full-period current/voltage matrix into a half-period matrix.

    This function transforms a data matrix representing full periods into one
    representing half periods. It uses the first half of each periods and the reversed
    second periods to create the half-cycle matrix.

    Args:
        data_mat (np.ndarray): A 2D array where each column represents a full period of data.
        period (int): The length of one period in terms of rows.

    Returns:
        np.ndarray: A 2D array representing the half-period matrix.

    Raises:
        AssertionError: If the input data matrix is not a full period, as checked by
                        `utils.check_if_array_is_full_cycle`.
    """
    utils.check_if_array_is_full_cycle(data_mat, period)

    data_mat_long = np.hstack(
        [data_mat[: period // 2, :], np.flip(data_mat[-period // 2 :, :], axis=0)]
    )
    return data_mat_long


def get_full_cycle_mat(a: np.ndarray) -> np.ndarray:
    """Converts a half-period matrix into a full-period matrix."""
    return np.vstack(
        [
            get_swing(a, True),
            np.flip(get_swing(a, False)),
        ]
    )


def fit_centered_parabola(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Fits parabola with a fixed vertex.

    Fits a parabola to the events with its peak fixed at the midpoint of the x
    events.

    This function fits a parabola of the form y = a * x^2 + bx + c to the
    given `x` and `y` events, with the vertex of the parabola constrained to lie
    at the midpoint of the `x` events. It assumes that the events points are evenly
    distributed along the `x` axis.

    Args:
        x (np.ndarray): The x-values of the events points.
        y (np.ndarray): The y-values of the events points.

    Returns:
        float: The coefficient `a` of the quadratic term.
        float: The coefficient `b` of the linear term.
        float: The coefficient `c` of the constant term.
    """

    vertex_x = (x[0] + x[-1]) / 2

    def parabola(x, a, c):
        return a * x**2 + -2 * a * vertex_x * x + c

    popt, pcov = scipy.optimize.curve_fit(parabola, x, y)

    a, c = popt

    return a, -2 * a * vertex_x, c


def get_parabola_vertex_y(a: float, b: float, c: float) -> float:
    """
    Calculates the y-coordinate of the vertex of a parabola.

    This function computes the y-coordinate of the vertex of a parabola given its
    coefficients `a`, `b`, and `c`, where the parabola is expressed as `a * x^2 + b * x + c`.

    Args:
        a (float): The coefficient of the quadratic term.
        b (float): The coefficient of the linear term.
        c (float): The constant term.

    Returns:
        float: The y-coordinate of the vertex of the parabola.

    Raises:
        ZeroDivisionError: If `a` is zero, as it would result in division by zero.
    """
    return -(b**2) / 4 / a + c


def full_cycle_mat_to_array(mat: np.ndarray) -> np.ndarray:
    """
    Converts a full-period matrix into a flattened array, removing NaN values.

    This function takes a 2D matrix representing full-period data, flattens it into a
    1D array, and removes any NaN values.

    Args:
        mat (np.ndarray): A 2D array where each row represents data for a full period.

    Returns:
        np.ndarray: A 1D array containing the flattened and NaN-filtered data.
    """
    data = mat.T.flatten()
    return data[~np.isnan(data)]


def get_compensated_conductance(
    v: np.ndarray,
    i: np.ndarray,
    period: int,
    phase: int,
    low_voltage: float = 95,
    high_voltage: float = 205,
    phase_offset=3,
) -> tuple[np.ndarray, np.ndarray]:
    """Gets the compensated conductance and voltage as half-period matrices.

    Requires a known period and phase.
    """
    v_mat, i_mat_comp = get_compensated_current(
        v,
        i,
        period,
        phase,
        low_voltage=low_voltage,
        high_voltage=high_voltage,
        phase_offset=phase_offset,
    )

    g_mat = get_conductance(i_mat_comp, v_mat)
    return (
        v_mat,
        g_mat,
    )


def interpolate(
    v_mat: np.ndarray, g_mat: np.ndarray, v_ref: np.ndarray = None
) -> np.ndarray:
    """Interpolate G(V) data to a reference set of voltages."""


    if v_ref is None:
        v_ref = SPACING_DNA["v"]

    if np.any(np.diff(v_ref) > 0):
        raise ValueError(
            "The reference voltage array must be monotonically decreasing (this corresponds to monotonically increasing nucleotide positions.)"
        )

    v_ref = np.flip(v_ref)

    g_mat_interp = np.full((len(v_ref), g_mat.shape[1]), np.nan)
    for j, (v, g) in enumerate(zip(v_mat.T, g_mat.T)):
        v = np.flip(v)  # From low to high voltages
        g = np.flip(g)

        mask = ~np.isnan(v) & ~np.isnan(g)  # Exclude NaN

        if not np.any(mask):  # All NaN
            continue

        # Test values in range of v_ref. Don't care that values are not
        # monotonically increasing outside this range.
        not_increasing = mask & (v >= np.min(v_ref)) & (v <= np.max(v_ref))
        not_increasing = (np.diff(v, prepend=0) < 0) & not_increasing

        n_excluded = np.sum(not_increasing)
        if n_excluded > 10:
            warnings.warn(
                f"Removing {n_excluded} voltage sample(s) that are not monotonically increasing. "
            )
        mask = mask & ~not_increasing

        g_mat_interp[:, j] = np.interp(
            v_ref, v[mask], g[mask], left=np.nan, right=np.nan
        )

    return np.flip(g_mat_interp, axis=0)


def matrix_as_df(g_mat: np.array, step: int = 0) -> pd.DataFrame | None:
    """Convert a conductance matrix into a conductance DataFrame.

    Expects each column of the conductance matrix to have an equal voltage basis.
    To ensure this, use capcomp.interpolate.

    Skips all-NaN columns in matrix.

    Args:
        g_mat: Conductance matrix to convert.
        step: Step number. Defaults to 0.

    Returns:
        A DataFrame with a multi-indexed rows with steps as level 0 and half-period number as level 1 containing
            conductance data.

    """
    mask = ~np.all(np.isnan(g_mat), axis=0)
    g_mat = g_mat[:, mask]

    columns = range(g_mat.shape[0])

    index = pd.MultiIndex.from_product(
        [[step], range(g_mat.shape[1])], names=["step", "period"]
    )

    return pd.DataFrame(g_mat.T, index=index, columns=columns)


def plot_g_df(
    g_df: pd.DataFrame,
    fig: plt.Figure = None,
    ax: plt.Axes = None,
    std=True,
    spacing_x=None,
    offset_x=0,
    **kwargs,
):
    """Plots a conductance DataFrame."""

    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=config.FIGSIZE_WIDE, dpi=config.DPI)

    if isinstance(spacing_x, str) and spacing_x.lower() == "dna":
        spacing_x = SPACING_DNA["x"]

    color = kwargs.pop("color", None)

    if isinstance(color, (list, tuple, np.ndarray)):
        if len(color) != g_df.nano.n_steps:
            raise ValueError(
                "To use a list of colors, the list must equal the number of steps in the dataframe."
            )
        colors = color
    else:
        colors = [color] * g_df.nano.n_steps

    n_steps = g_df.nano.n_steps
    feat_size = g_df.nano.n_features

    x_mat = get_plot_x(feat_size, n_steps, spacing_x)
    x_mat += offset_x

    alpha = kwargs.pop("alpha", 1)
    for j, g_mat in g_df.nano.iter_matrices():
        color = colors[j]

        x = x_mat[j, :]
        mu = np.nanmean(g_mat, axis=1)
        line = ax.plot(x, mu, alpha=alpha, color=color, **kwargs)

        if std:
            sigma = np.nanstd(g_mat, axis=1)
            ax.fill_between(
                x,
                mu - sigma,
                mu + sigma,
                alpha=alpha * 0.3,
                zorder=0,
                color=color if color is not None else line[0].get_color(),
                **kwargs,
            )

    if spacing_x is None:
        ax.set_xlabel("Observed step number")
    else:
        ax.set_xlabel("DNA position (nt)")

    ax.set_ylabel(r"Conductance (nS)")

    fig.tight_layout()

    return fig, ax


def get_plot_x(feat_size: int, n_steps: int, spacing_x: int) -> np.ndarray:
    """Get x-axis for a variable voltage plot"""
    if spacing_x is None:
        x_mat = (np.arange(n_steps * feat_size) / feat_size).reshape(
            (n_steps, feat_size)
        )
    else:
        if len(spacing_x) != feat_size:
            raise ValueError(
                f"The x-spacing array must have the same size as the features. "
                f"Got a spacing array of length {len(spacing_x)} but features "
                f"of size {feat_size}."
            )

        x_mat = np.arange(n_steps) * config.MOTOR_STEP_SIZE
        x_mat = np.reshape(x_mat, (x_mat.size, 1)) + spacing_x
    return x_mat

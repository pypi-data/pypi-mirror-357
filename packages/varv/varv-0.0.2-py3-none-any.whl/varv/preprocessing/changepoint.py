# Created by Henry Brinkerhoff
# Written for Python by Thijn Hoekstra

"""Change point detection

"""
import copy
import dataclasses
import warnings
from collections.abc import Iterator
from importlib import resources as impresources

import scipy
import numpy as np
import pandas as pd

from varv import utils
from varv.preprocessing import assets, cpic, capcomp, capnorm
from varv.feature_extraction import dimreduction, removal_filter, recombination_filter

inp_file_level_finding = (
    impresources.files(assets) / "principal_components_for_level_finding.npy"
)

BASIS_FNS_LEVEL_FINDING = np.load(inp_file_level_finding)


def get_bias_period_and_phase(
    v_data: np.ndarray, max_length_to_check: int = 10000, verbose=False
) -> tuple:
    """

    Gets the bias frequency period in samples and its phase from samples
    without the need for knowing the bias frequency *a priori*. Assumes that
    the bias frequency is the frequency in the signal with the largest
    amplitude.

    Args:
        v_data (np.ndarray): A numpy array containing the time series of bias
            voltage.
        max_length_to_check (int): Maximum number of samples in which to find a
            period and phase. Defaults to 10,000 samples. Speeds up Fourier
            transform.
        verbose (bool): Whether to print information on the found frequency.
            Defaults to False.

    Returns:
        A tuple containing the period and the phase of the most prominent
        frequency in the signal.

    """

    N = min(max_length_to_check, len(v_data))

    # Find the phase from the voltage assets
    y = v_data[:N]
    yf = scipy.fft.fft(y)[: N // 2]
    xf = scipy.fft.fftfreq(N)[: N // 2]
    idx = np.argmax(np.abs(yf)[1:]) + 1  # Skip DC component

    fourier_component = yf[idx]

    period = round(1 / xf[idx])

    if verbose:
        print(f"Found a frequency component with a period of " f"{period} samples.")

    if np.abs(fourier_component) < np.mean(np.abs(yf)):
        raise ValueError(
            f"No AC voltage applied in first {N} points of file - could not "
            f"determine phase."
        )

    phase = utils.get_phase_from_fourier_component(fourier_component, period)
    return period, phase


@dataclasses.dataclass
class Cumulative:
    r"""Class for calculating means from a cumulative sum.

    Consider an array $x = x_1, x_2, \dots x_n$ and its cumulative sum
    $X = x_1, x_1 + x_2, \dots x_1 + x_2 + \dots + x_n$. Using the cumulative sum, the
    means for some range in that array can be efficiently calculated. For example, take a series
    $x = 1, 4, 4,  2, -1,  0,  1,  2, -3$, which has a cumulative sum:
    $X = 1, 5, 9, 11, 10, 10, 11, 13, 10$. To find the sum for the values from $x_1$ to $x_7$,
    we subtract $X_7$ from $X_1$ and divide by the number of points, i.e. 13 - 1 = 12.
    Note that this equivalent to $ + 4 + 2 + -1 + 0 + 1 + 2 = 12$. This is useful for calculating
    many means without having to re-add all the values ever time.

    Attributes:
        values: A NumPy array containing the cumulative sum.
        l: Sum to the left of some index.
        r: Sum to the right of some index.
        t: Sum of the whole range.

    """

    values: np.ndarray
    l: np.ndarray = None
    r: np.ndarray = None
    t: np.ndarray = None

    def calculate_means(
        self, left: int, right: int, n_l: np.ndarray = None, n_r: np.ndarray = None
    ) -> None:
        """Calculates the sums over three subsets of some in the data.

        Sums are calculated the range from indices `left` to `right`. Consider an index `C` in this range
        dividing the range into having `n_l` points between `left` and `C`.
        Similarly, there are `n_r` points between `C` and `right`. This function calculates the
        sum of all the points `left` and `C`, along with those between `C` and `right`, and also
        calculates the sum of all the values in the range from indices `left` to `right`.

        Note that instead of a single `n_l`, we are interested in a whole range of possible `n_l`s.
        The same goes for `n_r`.

        This is used for fast calculation of means without re-adding values.

        Args:
            left: Index denoting the left of a range of interest.
            right: Index denoting the right of a range of interest.
            n_l: Sizes of the left subdivision of that range to be summed.
            n_r: Sizes of the right subdivision of that range to be summed.
        """
        if n_l is None and n_r is None:
            # Calculate mean for full range from left to right
            n_l = np.arange(right - left + 1)
            n_r = np.flip(n_l)

        if np.min(n_l) < 0 or np.max(n_l) > (right - left):
            raise IndexError(
                f"Cannot calculate means with number of points ranging from "
                f"{np.min(n_l)} to {np.max(n_l)} for data between {left} and "
                f"{right} ({right - left} data points.)"
            )

        self.l = self.values[..., left + n_l] - self.values[..., [left]]
        self.l[..., n_l == 0] = np.nan  # Mean of zero points is NaN

        self.r = self.values[..., [right]] - self.values[..., right - n_r]
        self.r[..., n_r == 0] = np.nan

        self.t = self.values[..., [right]] - self.values[..., [left]]


def get_cumulative_sums(
    x: np.ndarray, bf: np.ndarray
) -> tuple[Cumulative, Cumulative, Cumulative]:
    """Computes cumulative sums for a data and its basis functions.
    Parameters:
        bf (np.ndarray): A 2D array of basis functions, with shape (n_basis_functions, N), where `n_basis_functions` is
                          the number of basis functions and N is the number of data points.
        x (np.ndarray): A 1D array of data points for of length N which the cumulative sums are calculated.

    Returns:
        tuple: A tuple containing:
            - BB (np.ndarray): A matrix of cumulative sums of products of basis functions, with
                                shape (n_basis_functions, n_basis_functions, N).
            - XB (np.ndarray): A vector of cumulative sums of products of `x` and the basis functions,
                                with shape (n_basis_functions, N).
            - xsq (np.ndarray): A vector of cumulative sums of squares of `x`, with shape (N).
    """
    # cumulate of x^2
    x = np.concatenate([[0], x], axis=-1)
    xsq = np.cumsum(x**2)

    # Vector of cumulates of x*b_i
    bf = np.concatenate([np.zeros((bf.shape[0], 1)), bf], axis=-1)
    XB = np.cumsum(x * bf, axis=-1)

    # matrix of cumulates of b_i*b_j, the cumulate for each entry of the matrix
    # is a row of BB
    BB = np.cumsum(np.einsum("ij,kj->ikj", bf, bf), axis=-1)

    return Cumulative(BB), Cumulative(XB), Cumulative(xsq)


def get_var(
    n: np.ndarray | int,
    BB_mean,
    XB_mean,
    xsq_mean,
    out: np.array = None,
    apply_slice: slice = None,
) -> np.ndarray:
    """
    Calculates the variance for left, right, and total regions using the given matrices and data.

    The function computes the variance for each region with respect to its basis functions.

    Parameters:
        n (np.ndarray): Array of the number of data points in the left region for each interval.
        apply_slice: Apply a slice to
        xsq_mean:
        XB_mean:
        BB_mean:
        out:

    Returns:
        tuple: A tuple containing three arrays:
            - var: Variance for the left region.
            - var_R: Variance for the right region.
            - var_T: Total variance.

    """
    if out is None:
        var = np.atleast_1d(np.full_like(n, np.nan, dtype=np.float64))
    else:
        var = out

    n = np.atleast_1d(n)

    if apply_slice is None:
        s = np.s_[:]
    else:
        s = apply_slice

    var[s] = (
        xsq_mean[s]
        - np.squeeze(
            XB_mean.T[s, np.newaxis, :]
            @ np.linalg.solve(BB_mean[..., s].T, XB_mean.T[s, ..., np.newaxis])
        )
    ) / n[s]

    return var


class BasisFunctionStepFinder:

    def __init__(self, bf: np.ndarray, cpic_multiplier: float = 4):

        self.n_basis_functions = bf.shape[0]

        if self.n_basis_functions > 10:
            warnings.warn(f"Using {self.n_basis_functions} basis functions. This can be very slow. Consider using ~5 basis functions.")

        self.period = bf.shape[1]

        if self.period < 2:
            raise ValueError(
                "Period (minimum step size), which is the size of the second "
                "dimension of the basis functions must be at least 2."
            )

        self.cpic_multiplier = cpic_multiplier
        self.bf = np.asarray(bf, dtype=np.float64)
        self.BB = None
        self.XB = None
        self.xsq = None

    def get_cpic(
        self,
        n_l: np.ndarray,
        n_r: np.ndarray,
        n_t,
        var_l: np.ndarray,
        var_r: np.ndarray,
        var_t: np.ndarray,
        p_cpic: float,
    ) -> np.ndarray:
        """
        Calculates the CPIC (Cumulative Penalized Information Criterion) for model selection.

        The CPIC combines the variance terms of different regions (left, right, total) with a penalty
        for the number of basis functions, and an additional penalty term (p_cpic) scaled by a multiplier.

        Parameters:
            n_l (np.ndarray): The number of data points in the left region.
            n_r (np.ndarray): The number of data points in the right region.
            n_t (int): The total number of data points (N_L + N_R).
            var_l (np.ndarray): The variance of the left region.
            var_r (np.ndarray): The variance of the right region.
            var_t (float): The variance of the total region.
            p_cpic (float): The penalty term for model complexity, computed based on the number of data points.

        Returns:
            np.ndarray: The calculated CPIC values.

        """

        if not np.all(n_l + n_r == n_t):
            raise ValueError(
                "The number of data points in the left region edded to those "
                "in the right region must be the same as the total number of "
                "data points at every index."
            )

        var_l[var_l <= 0] = 1e-15
        var_r[var_r <= 0] = 1e-15

        return (
            0.5 * (n_l * np.log(var_l) + n_r * np.log(var_r) - n_t * np.log(var_t))
            + self.n_basis_functions
            + self.cpic_multiplier * p_cpic
        )

    def find_transitions_local(self, left: int, right: int) -> np.array:
        empty_transitions = np.array([], dtype=np.int64)

        n_l, n_r, n_t = self.get_number_of_points(left, right)

        # If total number of points is smaller than two level lengths,
        # there are no candidate change points, so return.
        if len(n_l) <= 1:
            return empty_transitions

        scores_cpic = self.calculate_scores(left, right, n_l, n_r, n_t)

        idx = np.nanargmin(scores_cpic)
        min_score = scores_cpic[idx]
        idx = n_l[idx] + left

        # Continue binary search.
        if min_score < 0:
            return np.hstack(
                [
                    self.find_transitions_local(left, idx),
                    [idx],
                    self.find_transitions_local(idx, right),
                ]
            )
        else:
            return empty_transitions

    def calculate_scores(self, left, right, n_l, n_r, n_t):
        # Calculate the means for left, right, and total ranges.
        self.BB.calculate_means(left, right, n_l, n_r)
        self.XB.calculate_means(left, right, n_l, n_r)
        self.xsq.calculate_means(left, right, n_l, n_r)

        # Coarse variance calculation (only every period)
        s = slice(0, len(n_l), self.period)  # Make slice to mask
        var_l = get_var(n_l, self.BB.l, self.XB.l, self.xsq.l, apply_slice=s)
        var_r = get_var(n_r, self.BB.r, self.XB.r, self.xsq.r, apply_slice=s)
        var_t = get_var(n_t, self.BB.t, self.XB.t, self.xsq.t)

        # Score transitions
        p_cpic = cpic.get_cpic_penalty(n_t)
        scores_cpic = self.get_cpic(n_l, n_r, n_t, var_l, var_r, var_t, p_cpic)

        # Find best transition point
        idx = np.nanargmin(scores_cpic)

        # Refine search by calculating variance around preliminary transition
        # point.
        s = slice(max(idx - self.period, 0), min(idx + self.period, len(n_l)))
        var_l = get_var(n_l, self.BB.l, self.XB.l, self.xsq.l, out=var_l, apply_slice=s)
        var_r = get_var(n_r, self.BB.r, self.XB.r, self.xsq.r, out=var_r, apply_slice=s)

        # Re-score transitions
        scores_cpic = self.get_cpic(n_l, n_r, n_t, var_l, var_r, var_t, p_cpic)
        return scores_cpic

    def get_number_of_points(self, left, right):
        n_t = right - left
        n_l = np.arange(self.period, n_t - self.period + 1, dtype=np.int64)
        n_r = np.flip(n_l)
        return n_l, n_r, n_t

    def fit(self, data: np.ndarray):
        data = np.asarray(data, dtype=np.float64)
        n = len(data)

        # Tile basis functions to same length as signal. Assume phase
        # difference has been removed.
        bf = tile_bf_to_match_signal(self.bf, n)

        self.BB, self.XB, self.xsq = get_cumulative_sums(data, bf)

        # Find
        transitions = self.find_transitions_local(0, n)

        transitions = np.sort(np.unique(transitions))
        return np.concatenate([[0], transitions, [n]], dtype=np.int32)


def remove_rises(data: np.array, period: int, phase: int, width: int = 21):

    delete_x = np.arange(phase - period, len(data) + period, period // 2)
    delete_x = delete_x.reshape((len(delete_x), 1))
    delete_y = np.arange(width)
    pts_to_delete = delete_x + delete_y  # Broadcasted
    pts_to_delete = pts_to_delete.flatten()
    pts_to_delete = pts_to_delete[
        (pts_to_delete >= 0) & (pts_to_delete <= len(data) - 1)
    ]

    original_length = len(data)
    original_indices = np.arange(original_length)

    data = np.delete(data, pts_to_delete)
    original_indices = np.delete(original_indices, pts_to_delete)

    period = period - 2 * width
    phase = phase - np.sum(pts_to_delete < phase)

    return data, original_indices, original_length, period, phase


def transitions_in_original_indices(transitions, original_indices, n: int):
    return np.concatenate(
        [[0], original_indices[transitions[1:-1]], [n]], dtype=np.int64
    )


def find_transitions(
    i_data: np.ndarray,
    period: int,
    phase: int,
    basis_fns: np.ndarray = None,
    n_basis_functions: int = 5,
    sensitivity: float = 1,
) -> np.ndarray[int]:
    """
    Finds step transitions in a time series using a combination of basis
    functions and statistical fitting.

    Args:
        phase:
        i_data (np.ndarray): A numpy array containing the time series of ionic
            current.
        period (int): Period of the bias frequency in samples.
        basis_fns (np.ndarray): An (M, N) numpy array containing N 1D basis
            functions of length M that describe the signal in between steps.
        sensitivity (float, optional): Sensitivity of the step finder. Default
            is 1.0.

    Returns:
        np.ndarray: An array of indices where the transitions occur.


    TODO: Allow for variable period size.
    """

    assert isinstance(period, int)

    if basis_fns is None:
        basis_fns = BASIS_FNS_LEVEL_FINDING[:, :n_basis_functions]  # First 5 Bfs

    # Forward phase by half a period to stick with convention from Noakes 2019.
    phase = copy.copy(phase)
    phase = (phase - period // 2) % period + 1

    # Define the number determining level finder sensitivity
    cpic_multiplier = sensitivity

    # Remove rises
    n = len(i_data)
    i_data, original_indices, original_length, period, phase = remove_rises(
        i_data, period, phase
    )

    # Define basis functions
    bf = add_phase_to_bf(basis_fns.T, phase)

    step_finder = BasisFunctionStepFinder(bf, cpic_multiplier)

    # Call the recursive level finding function
    transitions = step_finder.fit(i_data)

    return transitions_in_original_indices(transitions, original_indices, n)


def tile_bf_to_match_signal(bf: np.ndarray, n: int) -> np.ndarray:
    """Repeats the basis functions.

    Tiles the basis functions so as to lengthen the array to a length equal
    to the current arrays.

    Args:
        bf (np.ndarray): An array containing the basis functions.
        n (int): The length of the current arrays.

    Returns:
        np.ndarray: An array containing repats of the basis functions that
            matches the length of the ionic current arrays.

    """
    return np.tile(bf, (1, (n // bf.shape[0]) + 1))[:, :n]


def add_phase_to_bf(basis_fns: np.ndarray, phase: int, seg: int = 0) -> np.ndarray:
    """Applies a phase shift to the basis functions.

    Shifts the basis functions by a certain phase so that they are corrected
    for the phase of the signal.

    Args:
        basis_fns (np.ndarray): An array containing the basis functions.
        phase (int): Phase shift of the current and voltage arrays in samples.
            Phase is zero corresponds to the voltage rising exactly at the
            first sample.
        seg: Reference point for phase. Defaults to zero. Not used. Originally
            used for dealing with arrays chunks.

    Returns:
        np.ndarray: The basis functions array corrected for phase.

    """
    bf = np.roll(basis_fns, phase - seg, axis=1)
    return bf


def iter_transitions(transitions: np.ndarray[int]) -> Iterator[int, int, int]:
    for j, (start, stop) in enumerate(zip(transitions[:-1], transitions[1:])):
        yield j, start, stop


def get_step_conductances(
    i_data,
    v_data,
    period=250,
    sensitivity=1,
    verbose=False,
    n_basis_functions_cp: int = 5,
    n_basis_functions_dr: int = 3,
    broad_v_range_min: float = 95,
    broad_v_range_max: float = 205,
    v_basis=None,
    phase_offset: int = 2,
) -> tuple[np.ndarray, pd.DataFrame]:
    """
    Identifies transitions and computes feature vectors based on capacitance compensation.

    This function finds the transitions between steps in the current and voltage data, performs
    capacitance compensation.

    Parameters:
        i_data (np.ndarray): Array containing the current data.
        v_data (np.ndarray): Array containing the voltage data.
        period (int, optional): The period of the data, default is 250.
        sensitivity (float, optional): Sensitivity factor for the transition detection, default is 1.
        verbose (bool, optional): Whether to print detailed information, default is False.
        n_basis_functions_cp (int, optional): Number of basis functions for capacitance compensation, default is 5.
        n_basis_functions_dr (int, optional): Number of basis functions for dimension reduction, default is 3.
        broad_v_range_min (float, optional): Lower voltage threshold for compensation, default is 95.
        broad_v_range_max (float, optional): Higher voltage threshold for compensation, default is 205.
        phase_offset (int, optional): Phase offset for compensation, default is 2.

    Returns:
        tuple: A tuple containing:
            - np.ndarray: Transitions between different steps.
            - np.ndarray: Feature vectors for each transition.
    """

    i_data = np.asarray(i_data)
    v_data = np.asarray(v_data)


    transitions, phase = get_transitions(
        i_data, v_data, period, sensitivity=sensitivity, return_phase=True
    )

    transitions, g_df = apply_capcomp_to_transitions(
        v_data, i_data, transitions, period, phase
    )

    return transitions, g_df


def get_transitions(
        i_data: np.ndarray,
        v_data: np.ndarray,
        period: int,
        sensitivity: float = 1,
        n_basis_functions_cp: int = 5,
        verbose: bool = False,
        return_phase: bool = False,
):
    """Gets transitions without needing to input phase"""
    phase = utils.get_phase_of_period(v_data, period)

    if verbose:
        print(f"Found frequency with period {period} with a phase {phase}.")

    transitions = find_transitions(
        i_data,
        period,
        phase,
        n_basis_functions=n_basis_functions_cp,
        sensitivity=sensitivity,
    )
    if return_phase:
        return transitions, phase
    else:
        return transitions


def apply_capcomp_to_transitions(
    v_data: np.ndarray,
    i_data: np.ndarray,
    transitions: np.ndarray,
    period: int,
    phase: int,
    strict=False,
) -> tuple[np.ndarray, pd.DataFrame]:

    kept_idxs = np.ones_like(transitions, dtype=bool)

    g_df = None
    k = 0
    for j, start, stop in iter_transitions(transitions):
        s = slice(start, stop)
        v_step = v_data[s]
        i_step = i_data[s]

        try:
            v_step, g_step = capcomp.get_compensated_conductance(
                v_step, i_step, period, (start - phase) % period
            )
        except capcomp.CapacitanceCompensationError as e:
            message = f"Could not apply capacitance compensation to step {j} starting at index {start} of length {stop - start}"
            if strict:
                raise capcomp.CapacitanceCompensationError(message) from e
            else:
                warnings.warn(message)
                kept_idxs[j] = False
                continue

        g_step = capcomp.interpolate(v_step, g_step, capcomp.SPACING_DNA["v"])

        if np.isnan(g_step).all(axis=1).any():
            kept_idxs[j] = False
            continue  # Skips steps that do not have a full period

        df = capcomp.matrix_as_df(g_step, step=k)

        g_df = pd.concat([g_df, df])

        k += 1
    return transitions[kept_idxs], g_df


def format_steps_df(
    transitions: np.ndarray, feature_df: pd.DataFrame, sfreq: float
) -> pd.DataFrame:
    steps_df = feature_df.copy()

    # Remove transitions indexes for steps removed by removal/recombination filter.
    steps_df["start_idx"] = transitions[:-1][feature_df.index]
    steps_df["stop_idx"] = transitions[1:][feature_df.index]

    steps_df["n_pts"] = steps_df["stop_idx"] - steps_df["start_idx"]
    steps_df["dwell_time_s"] = steps_df["n_pts"] / sfreq

    steps_df["start_idx"].astype(int)
    steps_df["stop_idx"].astype(int)
    steps_df["n_pts"].astype(int)

    return steps_df


def get_step_df(
        i: np.ndarray,
        v: np.ndarray,
        sfreq: float,
        period: int,
        min_steps: int = 5,
        remove: bool = True,
        recombine: bool = True,
        **kwargs
) -> pd.DataFrame | None:
    transitions, g_df = get_step_conductances(
        i,
        v,
        period,
        **kwargs,
    )
    n_steps_original = g_df.nano.n_steps


    if remove:
        remover = removal_filter.RemovalFilter()
    else:
        # Removal filter automatically does preprocessing, so just one once, which will not remove any features.
        remover = removal_filter.RemovalFilter(max_iter=1)

    remover.fit(g_df)
    g_df = remover.predict()

    if g_df.nano.n_steps < min_steps:
        warnings.warn(
            f"Fewer than {min_steps} steps left after removal filter. Started "
            f"from {n_steps_original}. Aborting.")
        return None

    n_steps_original = g_df.nano.n_steps

    if recombine:
        recombiner = recombination_filter.RecombinationFilter()
        recombiner.fit(g_df)
        feature_df = recombiner.predict_features()
    else:
        # If not recombining, just get the features out of the removal
        # filter.
        feature_df = remover.predict_features()

    if feature_df.nano.n_steps < min_steps:
        warnings.warn(
            f"Fewer than {min_steps} steps left after recombination filter. "
            f"Started from {n_steps_original} after removal filter. Aborting.")
        return None

    return format_steps_df(transitions, feature_df, sfreq)

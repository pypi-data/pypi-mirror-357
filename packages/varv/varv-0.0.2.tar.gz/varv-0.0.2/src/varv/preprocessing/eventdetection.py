# Created by Ruben Marchau
# Refactored and documented by Thijn Hoekstra
from typing import Optional

import scipy
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

from varv import base, utils


class OpenStateNotFoundError(Exception):
    pass


class EventDetectionFailure(Exception):
    pass


def select_component_by_range(
    components: list[scipy.stats.norm],
    weights: np.ndarray,
    lower_bound: float,
    upper_bound: float,
):
    """Selects most abundant Gaussian component

    Selects the most abundant Gaussian component within a specified range of
    means.

    This function takes the means, standard deviations, and weights of
    Gaussian components and selects the component with the highest weight
    (most abundant) whose mean lies between `lower_bound` and `upper_bound`.
    If no components are found in this range, it returns `None`.

    Args:
        weights:
        components:
        lower_bound (float): The lower bound for the range of acceptable
            component means.
        upper_bound (float): The upper bound for the range of acceptable
            component means.

    Returns:

    """

    # Filter components within the specified range
    valid_indices = [
        j
        for j, comp in enumerate(components)
        if lower_bound < comp.mean() < upper_bound
    ]

    if len(valid_indices) == 0:
        return None  # No components in the specified range

    # Select the component with the highest weight
    idx = valid_indices[np.argmax(weights[valid_indices])]
    return components[idx]


def sort_components(
    components: list[scipy.stats.norm], weights: np.ndarray = None
) -> tuple[scipy.stats.norm, np.array] | list[scipy.stats.norm]:
    """Sorts Gaussian components by their means in descending order.

    This function takes the means, standard deviations, and weights of Gaussian
    components and sorts them in descending order based on the means. The
    standard deviations and weights are reordered accordingly to match the
    sorted means.

    Args:
        weights:
        components:

    Returns:
        tuple: A tuple containing:
            - sorted_means (np.ndarray): The means of the Gaussian components
                sorted in descending order.
            - sorted_stds (np.ndarray): The standard deviations sorted to match
                the sorted means.
            - sorted_weights (np.ndarray): The weights sorted to match the
                sorted means.
    """
    # Sort for weights
    means = [comp.mean() for comp in components]
    idxs = np.argsort(means)[::-1]

    # Sort components
    components.sort(key=lambda c: c.mean(), reverse=True)

    if weights is None:
        return components
    else:
        return components, weights[idxs]


def get_open_state_mask(
    i: np.ndarray, component: scipy.stats.norm, extent: float = 0.9999
) -> np.ndarray:
    """Generates a boolean mask identifying the open pore state

    This function computes a boolean array that marks the current _events points
    belonging to the open pore state. It uses the mean and standard deviation
    from the provided `open_state_component` (Gaussian component) to calculate
    current values that fall inside a confidence interval defined by
    `extent` (default 99.99%) and creates a mask based on the _events within that
    interval.

    Args:
        component:
        i (np.ndarray): The current trace
        extent (float, optional): The confidence interval for defining the
            open pore state. Default is 0.9999 (99.99%).


    Returns:
        np.ndarray: A boolean array where `True` indicates the _events points
        within the open pore state.
    """

    q_low = component.ppf(0.5 - extent / 2)
    q_high = component.ppf(0.5 + extent / 2)

    return (i >= q_low) & (i <= q_high)


def find_open_state(
    raw: base.Raw,
    lower_bound: float = 220,
    upper_bound: float = 250,
    lowpass: float = None,
    n_components: int = 3,
    extent=0.9999,
    resample_to_freq: float = None,
    max_samples: int = None,
    verbose: bool = False,
) -> None:
    """Mark the open state of a measurement

    This function identifies the open pore state of a Raw by applying
    a Gaussian mixture model to the current _events and determining the Gaussian
    component representing the open state current distribution. This component
    must lie within the specified bounds (`lower_bound` to `upper_bound`). It
    then generates a boolean mask for the open state within a confidence
    interval (`extent`), and marks the relevant _events points in the Raw.

    Args:
        lowpass: # TODO update docstring with reasample and lowpass filter
        resample_to_freq:
        raw (Raw): A Raw object.
        lower_bound (float, optional): The lower bound of the current range in
            which the open state curent must lie. Default is 220 pA.
        upper_bound (float, optional): The upper bound of the current range in
            which the open state curent must lie. Default is 220 pA.
        n_components (int, optional): The number of Gaussian components to fit.
            Default is 3.
        extent (float, optional): The confidence interval for defining the open
            pore state. Default is 0.9999 (99.99%). A higher number means a
            larger number of points will be assigned as being the open state
            current.

    Returns:
        None: The function modifies the Raw in place by assigning the
        open state to relevant _events points.

    Example:
        >>> raw = Raw()  # Assume this is a valid Raw object
        >>> find_open_state(raw,lower_bound=220,upper_bound=250,n_components=3,extent=0.9999)
        >>> print(raw.state)  # Raw will have the open states marked
    """
    raw.reset_states()

    i_original = raw.i
    i = raw.i.copy()
    if resample_to_freq:
        i = utils.downsample_by_poly(resample_to_freq, raw.info.sfreq, i)
    i = shorten_data_to_ends(i, max_samples)

    if verbose:
        print_resampling_and_shortening(len(i), len(raw), resample_to_freq)

    if lowpass is not None:
        i = utils.lowpass_filter(i, raw.info.sfreq, lowpass)
        i_original = utils.lowpass_filter(i_original, raw.info.sfreq, lowpass)

    components, weights = get_gmm(i, n_components=n_components)
    component = select_component_by_range(components, weights, lower_bound, upper_bound)

    if component is None:
        raise OpenStateNotFoundError(
            f"Could not find a current distribution within the bounds "
            f"({lower_bound}, {upper_bound}) pA. Found components have means "
            f"at {', '.join(np.round([comp.mean() for comp in components] , 1).astype(str))}. "
            f"Try checking the data or changing the ranges."
        )

    mask = get_open_state_mask(i_original, component, extent=extent)

    raw["state", mask] = base.OPEN_STATE


def print_resampling_and_shortening(new_length, old_length, resample_to_freq):
    shortened = new_length > old_length
    print(f"Original data has {old_length} samples. ", end="")
    if shortened and resample_to_freq:
        print(
            f"Resampled data to {resample_to_freq:.0f} Hz and shortened "
            f"to {new_length} samples. ",
            end="",
        )
    elif not shortened and resample_to_freq:
        print(f"Resampled data to {resample_to_freq:.0f} Hz. ", end="")
    elif shortened:
        print(f"Shortened data to {new_length} samples. ", end="")
    else:
        print("Using all data. ", end="")
    print(
        f"Continuing with {new_length}/{old_length} "
        f"({new_length / old_length:.0%}) samples. ",
        end="",
    )


def shorten_data_to_ends(a, max_samples):
    if max_samples and max_samples < len(a):

        a = np.concatenate([a[: max_samples // 2], a[-max_samples // 2 :]])
    return a


def get_gmm(
    x: np.ndarray, n_components: int = 3, ignore_range: Optional[tuple] = None
) -> tuple[list[scipy.stats.norm], np.ndarray]:
    if ignore_range:
        x = x[(x < min(ignore_range)) | (x > max(ignore_range))]

        mean = sum(ignore_range) / 2
        scale = max(ignore_range) - mean
        good_component = scipy.stats.uniform(loc=mean - scale, scale=scale * 2)

        n_components -= 1  # Need to look for 1 fewer component
    else:
        good_component = None

    clf = GaussianMixture(n_components=n_components, random_state=0)
    clf.fit(x.reshape(-1, 1))
    components = [
        scipy.stats.norm(mean[0], np.sqrt(var)[0, 0])
        for mean, var in zip(clf.means_, clf.covariances_)
    ]
    weights = clf.weights_

    if ignore_range:
        components.insert(0, good_component)
        weights = np.concatenate([[1], weights])

    return components, weights


def get_bad_voltage_mask(v: np.ndarray, distr_good_voltage, distr_rest):
    p_normal = distr_good_voltage.pdf(v)
    p_rest = np.max(np.vstack([g.pdf(v) for g in distr_rest]), axis=0)

    return p_rest > p_normal


def find_bad_voltages(
    raw: base.Raw,
    n_components: int = 3,
    ignore_range: Optional[tuple] = None,
    resample_to_freq: float = 5000,
    max_samples: int = None,
    verbose: bool = False,
) -> None:
    v = raw.v.copy()
    v = utils.downsample_by_poly(resample_to_freq, raw.info.sfreq, v)
    v = shorten_data_to_ends(v, max_samples)

    if verbose:
        print_resampling_and_shortening(len(v), len(raw), resample_to_freq)

    components, weights = get_gmm(
        v, n_components=n_components, ignore_range=ignore_range
    )
    components, weights = sort_components(components, weights)

    v_original = raw.v
    mask = get_bad_voltage_mask(v_original, components[0], components[1:])

    raw["state", mask] = base.BAD_VOLTAGE_STATE


def get_open_state_segments(raw: base.Raw):
    open_clean_state = raw.state == base.OPEN_STATE

    state_changes = np.diff(np.concatenate(([0], open_clean_state, [0])))

    if not np.any(state_changes):
        raise RuntimeError(
            "Did not find any states. Please run "
            "find_open_state() and find_bad_voltages() first."
        )

    # Find start and end indices
    starts = np.where(state_changes == 1)[0]
    ends = np.where(state_changes == -1)[0] - 1
    # Create DataFrame with segments

    segments = pd.DataFrame(
        {"start_idx": raw.data["i"].index[starts], "stop_idx": raw.data["i"].index[ends]}
    )

    return segments


def get_open_pore_fit(raw: base.Raw, degree: int = 1):
    open_clean_state = raw.state == base.OPEN_STATE

    if not np.sum(open_clean_state):
        raise ValueError("No samples marked as open state.")

    y = raw.i[open_clean_state]
    x = raw.get_time()[open_clean_state]

    return np.polynomial.Polynomial.fit(x, y, deg=degree)


def get_unique_states(raw: base.Raw):
    return np.unique(raw.state)


def get_events_idxs(raw: base.Raw, boundary_trim: int = 5):
    """

    Assumes the Raw state has been annotated with bad voltages and open
    pore voltages

    Args:
        boundary_trim (int):
        raw:

    Returns:

    """
    open_clean_state = raw.state == base.GOOD_STATE

    d = np.diff(open_clean_state.astype(int))

    start_indices = np.where(d == 1)[0] + 1
    end_indices = np.where(d == -1)[0]

    if open_clean_state[0] == 1:
        start_indices = np.insert(start_indices, 0, 0)
    if open_clean_state[-1] == 1:
        end_indices = np.append(end_indices, len(open_clean_state) - 1)

    start_indices += boundary_trim
    end_indices -= boundary_trim
    start_indices = np.clip(start_indices, 0, len(open_clean_state) - 1)
    end_indices = np.clip(end_indices, 0, len(open_clean_state) - 1)

    # Create a DataFrame from the start and end indices
    events_df = pd.DataFrame({"start_idx": start_indices, "stop_idx": end_indices})

    # Add a duration column
    events_df["n_samples"] = events_df["stop_idx"] - events_df["start_idx"] + 1

    # Remove negative length (due to trim) _events
    events_df = events_df[events_df["n_samples"] > 0]
    # Reset index
    events_df.reset_index(drop=True, inplace=True)

    return events_df

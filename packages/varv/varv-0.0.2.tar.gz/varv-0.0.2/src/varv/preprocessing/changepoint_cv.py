# Created by Cees Dekker Lab at the Delft University of Technology
# Refactored by Thijn Hoekstra
import copy
import itertools

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from varv import config
from varv.preprocessing import changepoint


def plot_steps_from_array(
    *args: tuple[np.ndarray, ...],
    std: np.ndarray = None,
    fig: plt.Figure = None,
    ax: plt.Axes = None,
    vlines_at_step: bool = False,
    spacing_x: float = 1,
    **kwargs,
):
    if fig is None and ax is None:
        fig, ax = plt.subplots(figsize=config.FIGSIZE_WIDE)

    color = kwargs.pop("color", None)

    if len(args) == 1:
        y = args[0]
        edges = (np.arange(len(y) + 1) - 0.5) * spacing_x
    elif len(args) == 2:
        edges = args[0]
        y = args[1]
    else:
        raise ValueError(
            "Must specify at least Y (step heights) or X and Y (step edges and step heights)"
        )

    if vlines_at_step:
        for edge in edges:
            ax.axvline(edge, color="black", alpha=0.1, linestyle="dashed")

    if isinstance(color, (list, tuple, np.ndarray)):
        if len(color) != len(y):
            raise ValueError(
                "To use a list of colors, the list must equal the number of steps."
            )
        start = 0
        for c, g in itertools.groupby(color):
            stop = start + len(list(g))

            plot_steps_segment(
                ax,
                y[start : min(stop + 1, len(y))],
                edges[start : min(stop + 2, len(edges))],
                std=False,
                color=c,
                **kwargs,
            )  # Plot line one extra step to make steps continuous
            if std is not None:
                plot_steps_segment(
                    ax,
                    y[start:stop],
                    edges[start : stop + 1],
                    std=std[start:stop],
                    color=c,
                    **kwargs,
                )  # Replot with std so filled areas aren't doubled up.

            start = stop
    else:
        if color is not None:
            kwargs["color"] = color  # Put back color
        plot_steps_segment(ax, y, edges, std=std, **kwargs)

    return fig, ax


def plot_steps_segment(ax: plt.Axes, y, edges, std=None, **kwargs):
    alpha = kwargs.pop("alpha", 1)
    line = ax.stairs(y, edges, baseline=None, alpha=alpha, **kwargs)

    if std is not None:
        kwargs.pop("color", None)
        ax.stairs(
            y + std,
            edges,
            baseline=y - std,
            fill=True,
            zorder=0,
            color=line.get_facecolor(),
            alpha=alpha * 0.1,
            **kwargs,
        )
    return line

def plot_bases(bases, size=None, fig: plt.Figure=None, ax: plt.Axes=None, **kwargs):
    if fig is None and ax is None:
        fig, ax = plt.subplots(figsize=config.FIGSIZE_WIDE)

    bases = copy.copy(bases)
    bases[0] = r"3$^\prime$-" + bases[0] + "   " # Padding to the text centers on the tickmark
    bases[-1] = "   " + bases[-1] + r"-5$^\prime$"

    x = (np.arange(len(bases)) - 0.25) * config.MOTOR_STEP_SIZE * 2 # Two steps per base

    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    ax.set_xticks(x, bases, fontfamily="monospace", fontsize=size)
    ax.set_yticks([])

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_bounds(x[0], x[-1])
    ax.spines['bottom'].set_visible(False)
    ax.set_ylim(-1, 0)

def plot_steps(
    steps: pd.DataFrame | np.ndarray,
    std=True,
    fig: plt.Figure = None,
    ax: plt.Axes = None,
    vlines_at_step=False,
    spacing_x: float | str = 1,
    **kwargs,
):
    """
    Plots a staircase plot with standard deviation shading for step-wise data.
    """

    colors = None
    if "color" in steps:
        colors = steps["color"].to_list()

    if isinstance(spacing_x, str) and spacing_x.lower() == "dna":
        spacing_x = config.MOTOR_STEP_SIZE

    fig, ax = plot_steps_from_array(
        steps["mean"].to_numpy(),
        std=steps["std"].to_numpy() if std else None,
        spacing_x=spacing_x,
        vlines_at_step=vlines_at_step,
        fig=fig,
        ax=ax,
        color=colors,
        **kwargs,
    )

    return fig, ax


def find_transitions(
    i_data: np.ndarray, min_level_length: int, sensitivity: float = 1
) -> np.ndarray:
    """Uses the variable voltage step finder with a flat basis function to find transitions.

    Args:
        i_data:
        min_level_length:
        sensitivity:

    Returns:

    """
    bf = np.atleast_2d(np.ones(min_level_length))
    step_finder = changepoint.BasisFunctionStepFinder(bf, sensitivity)

    return step_finder.fit(i_data)


def get_step_features(
    data: np.ndarray,
    sensitivity: float = 1,
    min_level_length: int = 2,
) -> tuple[np.ndarray, np.ndarray]:

    transitions = find_transitions(data, min_level_length, sensitivity)

    features = np.zeros((2, len(transitions) - 1))

    for j, start, stop in changepoint.iter_transitions(transitions):
        features[0, j] = np.mean(data[start:stop])
        features[1, j] = np.std(data[start:stop])

    return transitions, features


def format_steps_df(transitions, features, sfreq):
    """
    Formats a DataFrame containing information about steps and their properties.

    This function creates a DataFrame where each row represents a step, with columns
    for the start and end indices of each step, the number of points in each step,
    the dwell time in seconds, and the mean and standard deviation values of the features
    for each step. The function assumes that the `features` array contains mean values
    in the first row and standard deviation values in the second row.

    Parameters:
        transitions (array-like): The indices of the transitions marking the start and end of each step.
        features (array-like): A 2D array where the first row contains mean feature values,
                               and the second row contains standard deviation values for each step.
        sfreq (float): The sampling frequency (samples per second), used to calculate dwell time.

    Returns:
        pd.DataFrame: A DataFrame with columns for the start and end indices, the number of points,
                      the dwell time in seconds, and the mean and standard deviation of each step.

    """
    steps_df = pd.DataFrame(
        {
            "start_idx": transitions[:-1],
            "stop_idx": transitions[1:],
        }
    )
    steps_df["n_pts"] = steps_df["stop_idx"] - steps_df["start_idx"]
    steps_df["start_s"] = steps_df["start_idx"] / sfreq
    steps_df["dwell_time_s"] = steps_df["n_pts"] / sfreq
    steps_df["mean"] = features[0, :]
    steps_df["std"] = features[1, :]

    return steps_df


def get_step_df(i: np.ndarray, sfreq: float, **kwargs) -> pd.DataFrame:
    results = get_step_features(i, **kwargs)
    return format_steps_df(*results, sfreq=sfreq)

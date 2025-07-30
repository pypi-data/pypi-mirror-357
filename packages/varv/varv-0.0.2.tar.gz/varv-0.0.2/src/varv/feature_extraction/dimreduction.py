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
from collections.abc import Generator
from importlib import resources as impresources

import numpy as np
import pandas as pd
import scipy.linalg
from matplotlib import pyplot as plt

from varv import config
from varv.preprocessing import capcomp, capnorm
from varv.feature_extraction import assets
from varv.utils import get_cov_cols, get_coef_cols

inp_file_dim_red = impresources.files(assets) / "principal_components_dna.npy"

BASIS_FUNCTIONS_DNA = np.load(inp_file_dim_red)


def predict(p: np.ndarray, bf: np.ndarray) -> np.ndarray:
    return bf @ p


def get_cov_vec_size(cov_dim: int):
    """Gets size of the covariance matrix expressed as a vector.

    See Also:
        get_cov_dim_from_cov_vec_length: The inverse function.
    """
    return int(cov_dim * (cov_dim + 1) / 2)


def get_cov_dim_from_cov_vec_length(l: int):
    """Gets the size of the covariance matrix from its vector expression.

    See Also:
        get_cov_vec_size: The inverse function.

    """
    n = -0.5 + 0.5 * np.sqrt(1 + 4 * 2 * l)
    if n % 1:
        raise ValueError(
            f"Got the covariance as a {l}-"
            f"dimensional vector which cannot be the values "
            f"of the upper triangle of an NxN covariance matrix."
        )
    return int(n)


def cov_from_vector(cov_vec: np.ndarray) -> np.ndarray:
    """
    Converts a vector of upper triangular elements of a covariance matrix into a full covariance matrix.

    This function takes a 1D or 2D array of the upper triangular elements (including the diagonal) of one
    or more covariance matrices and reconstructs the full covariance matrices. The reconstructed matrix is
    symmetric, with the upper triangular elements filled from the provided vector and the lower triangular
    elements copied from the upper triangular ones.

    Parameters:
        cov_vec (np.ndarray): A 1D array containing the upper triangular elements of a covariance matrix
                               (including the diagonal), or a 2D array of such vectors.

    Returns:
        np.ndarray: A 2D array containing the full covariance matrix.

    Raises:
        ValueError: If the input array does not have the expected shape.
    """
    n = int(np.sqrt(len(cov_vec)))
    return cov_vec.reshape((n, n))


class DimensionReduction:

    def __init__(self, bf: np.ndarray = None):
        """

        Args:
            bf: (NxM) array where N is the length of the basis function and M is the number of basis functions.
        """
        if bf is None:
            bf = BASIS_FUNCTIONS_DNA

        self.bf = bf

        d = self.bf.shape[1]
        self.n_features = d
        self.cov = np.full((d, d), np.nan)
        self.p = np.full(d, np.nan)

        self.n_samples = None
        self.msd = None
        self.well_estimated = True
        self.msd_of_mean = None

    def fit(self, g_mat: np.ndarray) -> None:
        """
        Gets the component amplitudes and covariance matrix from the conductance matrix.

        This function calculates the component amplitudes by solving a least squares problem
        using the provided basis functions (bfs) and the conductance matrix (g_mat_long).
        It then computes the covariance matrix of the component amplitudes.

        Parameters:
            g_mat (np.ndarray): The NxM conductance matrix, which has M repeats of N conductance measurements per half
                period. Each column represents a different measurement or sample. Conductances
                should be ordered from high to low voltages (so from low to high position offsets).
        Returns:
            tuple: A tuple containing:
                - np.ndarray: The component amplitudes.
                - np.ndarray: The covariance matrix of the component amplitudes.
        """

        d = self.n_features
        n_half_cycle_samples = g_mat.shape[1]

        p = np.full((d, n_half_cycle_samples), np.nan)

        good_columns = ~np.any(np.isnan(g_mat), axis=0)
        self.n_samples = np.sum(good_columns)

        p[:, good_columns], res, rnk, s = scipy.linalg.lstsq(
            self.bf, g_mat[:, good_columns]
        )

        independent_entries = int(d * (d + 1) / 2)
        if self.n_samples < independent_entries:
            cov = np.full((d, d), np.nan)
            self.well_estimated = False
        else:
            cov = np.cov(p[:, good_columns])
            self.well_estimated = True

        self.cov = cov
        self.p = np.nanmean(p, axis=1)

        g_pred = self.predict()
        self.msd = np.nanmean(np.square(g_mat.T - g_pred))

    def predict(self) -> np.ndarray:
        """
        Reconstructs a signal from the component amplitudes and basis functions.

        This function computes the signal by multiplying the component amplitudes `p`.
        The result is the reconstituted signal
        which represents a combination of the components described by the basis functions.

        Parameters:
          p (np.ndarray): The component amplitudes to be used for signal reconstruction.

        Returns:
          np.ndarray: The reconstituted signal.
        """
        return predict(self.p, self.bf)

    def predict_std(self, n_draws: int = 1000) -> np.ndarray:
        """
        Estimates the variance of signal curves from a mean and covariance matrix.

        This function generates random signal curves based on the given mean and covariance matrix
        by sampling from a multivariate normal distribution. It then calculates the variance of these
        random curves at each point in the signal. The result is the estimated variance across the DNA positions.

        This is used for display purposes only. The Hidden Markov Model (HMM) uses the covariance matrix directly.

        Parameters:
            mean (np.ndarray): A 1D or 2D array representing the mean conductance curve(s).
            cov (np.ndarray): A 2D or 3D array representing the covariance matrix associated with the mean.
            n_draws (int, optional): The number of random draws to take from the multivariate normal distribution. Default is 100.

        Returns:
            np.ndarray: The estimated variance of the signal curves at each position.
        """
        if self.well_estimated:
            ps = np.random.multivariate_normal(self.p, self.cov, size=n_draws).T

            curves = predict(ps, self.bf)

            return np.std(curves, axis=1)

        else:
            return np.full(self.bf.shape[0], np.nan)

    @property
    def cov_vector(self) -> np.ndarray:
        """
        Get the upper triangular elements (including the diagonal) from a covariance matrix.

        This function returns a 1D array containing the elements of the upper triangular part of the covariance
        matrix (including the diagonal). The number of elements is given by N * (N + 1) / 2, where N is the
        dimensionality of the covariance matrix..

        Returns:
            np.ndarray: A 1D array containing the upper triangular elements of the covariance matrix.
        """
        return self.cov.flatten()

    @property
    def feature_vector(self) -> np.ndarray:
        """
        Combines a feature vector and a covariance vector into a single feature vector.

        This function concatenates the input vectors `x` (a feature vector) and `cov_vec` (a vector containing
        upper triangular elements of a covariance matrix) into a single 1D array, which can be used as a unified
        feature representation.

        Returns:
            np.ndarray: A 1D array obtained by concatenating `x` and `cov_vec`.

        """
        return np.hstack((self.p, self.cov_vector))

    @classmethod
    def from_feature_vector(cls, feature: np.ndarray, bf: np.ndarray = None):
        if bf is None:
            bf = BASIS_FUNCTIONS_DNA

        p_length = bf.shape[1]
        p = feature[:p_length]

        cov_vec_length = p_length**2

        cov = np.full((p_length, p_length), np.nan)
        if len(feature) == p_length:
            # Only has coefficients, no covariance
            pass
        elif cov_vec_length + p_length == len(feature):
            cov = cov_from_vector(feature[p_length : p_length + cov_vec_length])
        else:
            raise IndexError(
                f"Expected parameter size of {p_length} from basis function "
                f"shape ({bf.shape}), and a covariance vector of size "
                f"{cov_vec_length}, together creating an feature vector of "
                f"length {cov_vec_length + p_length}. Instead got "
                f"{len(feature)} columns labeled coefficient and.or covariance labels. Please check the formatting of "
                f"the feature DataFrame."
            )

        new_class = cls(bf)
        new_class.cov = cov

        if np.any(np.isnan(cov)):
            new_class.well_estimated = False

        new_class.p = p

        return new_class


class ReducedOffset(DimensionReduction):

    def fit(self, offset: float) -> None:

        d = self.n_features

        g_mat = np.full(len(self.bf), offset)

        self.p, res, rnk, s = scipy.linalg.lstsq(self.bf, g_mat)

        cov = np.full((d, d), np.nan)
        self.well_estimated = False

        self.cov = cov

        self.msd = 0


def offset_coef(offset: float, bf: np.ndarray = None) -> np.ndarray:
    reducer = ReducedOffset(bf)
    reducer.fit(offset)

    return reducer.p


def get_feature_df(g_df: pd.DataFrame, bfs: np.ndarray = None) -> pd.DataFrame:
    reducer = DimensionReduction(bfs)
    d = reducer.n_features

    feature_vector_size = len(reducer.feature_vector)
    columns = (
        get_coef_cols(d)
        + get_cov_cols(d)
        + ["mean", "std", "MSD_fit", "extreme", "n_samples", "well_estimated", "type"]
    )

    feat_df = pd.DataFrame(
        index=np.unique(g_df.index.get_level_values(0)), columns=columns
    )
    feat_df.index.set_names("step")

    for j, g_mat in g_df.nano.iter_matrices(label=True):
        reducer.fit(g_mat)

        feat_df.loc[j, columns[:feature_vector_size]] = reducer.feature_vector
        feat_df.loc[j, "mean"] = np.nanmean(g_mat)
        feat_df.loc[j, "std"] = np.nanstd(g_mat)
        feat_df.loc[j, "MSD_fit"] = reducer.msd
        feat_df.loc[j, "extreme"] = np.nanmax(np.abs(g_mat))
        feat_df.loc[j, "n_samples"] = reducer.n_samples
        feat_df.loc[j, "well_estimated"] = reducer.well_estimated
        feat_df.loc[j, "type"] = "DNA"

    feat_df = feat_df.astype({n: np.float64 for n in feat_df.columns[:-3]})
    feat_df = feat_df.astype({"n_samples": np.int64})
    feat_df = feat_df.astype({"well_estimated": bool})
    feat_df = feat_df.astype(
        {
            "type": pd.CategoricalDtype(
                categories=["DNA", "Linker", "Peptide"], ordered=True
            )
        }
    )

    return feat_df


def fill_ill_defined_covs(feature_df: pd.DataFrame, q: float = 90) -> pd.DataFrame:
    dets = get_dets(feature_df)

    dets_percentile = np.nanpercentile(dets, q)

    idx = np.nanargmin(np.abs(dets - dets_percentile))
    idx = feature_df.index[idx]

    cov_cols = feature_df.filter(like="cov_").columns
    feature_df.loc[~feature_df["well_estimated"], cov_cols] = feature_df.loc[
        idx, cov_cols
    ].to_numpy()

    return feature_df


def get_dets(feature_df):
    dets = np.full(feature_df.nano.n_steps, np.nan)
    for j, cov in feature_df.nano.iter_covs():
        if not np.isnan(cov).all():
            dets[j] = np.linalg.det(cov)
    return dets


def iter_predict(feature_df: pd.DataFrame, std=False, bf=None) -> Generator:
    n_features = feature_df.nano.n_features
    vecs = feature_df.iloc[:, : n_features + n_features**2].to_numpy()
    for j, vec in enumerate(vecs):

        reducer = DimensionReduction.from_feature_vector(vec, bf=bf)
        if std:
            yield reducer.predict(), reducer.predict_std()
        else:
            yield reducer.predict()


def calibrate_features(
    feature_df: pd.DataFrame | np.ndarray, bf=None, iqr_ref=None, median_ref=None
) -> pd.DataFrame:
    if bf is None:
        bf = BASIS_FUNCTIONS_DNA

    g_mat = predict(feature_df.nano.coefs.to_numpy().T, bf)

    iqr, median = capnorm.calibration_metrics(g_mat)

    scale, offset = capnorm.get_calibration_scale_and_offset(
        iqr, median, iqr_ref=iqr_ref, median_ref=median_ref
    )

    return apply_calibration(feature_df, scale, offset)


def apply_calibration(feature_df, scale, offset):
    """Use nanopore accessor to apply rescaling in basis function space"""
    return (feature_df.nano * scale).nano + offset


def plot_feature_df(
    feature_df: pd.DataFrame,
    bfs: np.ndarray = None,
    fig: plt.Figure = None,
    ax: plt.Axes = None,
    std=True,
    spacing_x: None | str | np.ndarray = None,
    dot=False,
    markeralpha=1,
    **kwargs,
):
    if not isinstance(feature_df, pd.DataFrame):
        raise TypeError(f"Features should be a DataFrame, got {type(feature_df)} instead")


    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=config.FIGSIZE_WIDE, dpi=config.DPI)

    if bfs is None:
        bfs = BASIS_FUNCTIONS_DNA

    if isinstance(spacing_x, str) and spacing_x.lower() == "dna":
        spacing_x = capcomp.SPACING_DNA["x"]

    if dot is True and spacing_x is not None:
        dot = np.argmin(np.abs(capcomp.SPACING_DNA["x"]))  # Put dot at index
    dot_size = kwargs.pop("markersize", None)

    n_steps = feature_df.nano.n_steps

    bf_size = bfs.shape[0]

    x_mat = capcomp.get_plot_x(bf_size, n_steps, spacing_x)

    alpha = kwargs.pop("alpha", 1)
    color = kwargs.pop("color", None)

    colors = None
    if isinstance(color, (list, tuple, np.ndarray)):
        if len(color) != n_steps:
            raise ValueError(
                "To use a list of colors, the list must equal the number of steps in the dataframe."
            )
        colors = color
    elif "color" in feature_df:
        colors = feature_df["color"].to_list()

    for j, (x, (mu, sigma)) in enumerate(zip(x_mat, iter_predict(feature_df, True, bf=bfs))):

        if colors is not None:
            c = colors[j]
        else:
            c = color

        line = ax.plot(x, mu, alpha=alpha, color=c, **kwargs)

        if std and not np.isnan(sigma).any():
            ax.fill_between(
                x,
                mu - sigma,
                mu + sigma,
                alpha=alpha * 0.1,
                zorder=0,
                color=c if color is not None else line[0].get_color(),
                edgecolor="none",
                **kwargs,
            )

        if dot is not False and spacing_x is not None:
            ax.scatter(x[dot], mu[dot], dot_size, alpha=markeralpha, color=c, **kwargs)

    if spacing_x is None:
        ax.set_xlabel("Observed step number")
    else:
        ax.set_xlabel("DNA position (nt)")

    ax.set_ylabel(r"Conductance (nS)")

    # fig.tight_layout()

    return fig, ax
